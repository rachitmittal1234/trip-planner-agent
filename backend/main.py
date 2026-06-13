import json
import asyncio
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from graph import graph

app = FastAPI(title="AI Trip Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex="https://.*.vercel.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    source: str = ""
    destination: str
    dates: str
    budget: str
    travel_style: str = "balanced"
    preferences: List[str] = []

class EditRequest(BaseModel):
    itinerary: dict = {}
    edit_note: str = ""

@app.get("/")
async def root():
    return {"message": "AI Trip Planner API is running"}

@app.post("/plan")
async def start_plan(request: TripRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "source": request.source,
        "destination": request.destination,
        "dates": request.dates,
        "budget": request.budget,
        "travel_style": request.travel_style,
        "preferences": request.preferences,
        "parallel_done": [],
        "retry_count": 0,
    }
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: list(graph.stream(initial_state, config=config, stream_mode="updates"))
    )
    return {"thread_id": thread_id, "status": "paused", "message": "Itinerary ready for review"}

@app.get("/status/{thread_id}")
async def get_status(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snapshot = graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Thread not found")
    state = snapshot.values
    next_node = list(snapshot.next) if snapshot.next else []
    return {
        "thread_id": thread_id,
        "next": next_node,
        "destination": state.get("destination"),
        "dates": state.get("dates"),
        "budget": state.get("budget"),
        "quality_score": state.get("quality_score"),
        "retry_count": state.get("retry_count"),
        "approval_status": state.get("approval_status"),
        "itinerary": state.get("itinerary"),
        "booking_confirmation": state.get("booking_confirmation"),
        "error": state.get("error"),
    }

@app.post("/approve/{thread_id}")
async def approve_plan(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    graph.update_state(config, {"approval_status": "approve"}, as_node="human_approval")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: list(graph.stream(None, config=config, stream_mode="updates"))
    )
    snapshot = graph.get_state(config)
    return {
        "thread_id": thread_id,
        "status": "approved",
        "booking_confirmation": snapshot.values.get("booking_confirmation")
    }

@app.post("/edit/{thread_id}")
async def edit_plan(thread_id: str, body: EditRequest):
    config = {"configurable": {"thread_id": thread_id}}
    graph.update_state(config, {
        "approval_status": "edit",
        "retry_count": 0,
        "error": body.edit_note or "User requested changes to the itinerary."
    }, as_node="human_approval")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: list(graph.stream(None, config=config, stream_mode="updates"))
    )
    return {"thread_id": thread_id, "status": "edited", "message": "Itinerary updated and re-checked"}

@app.post("/reject/{thread_id}")
async def reject_plan(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    graph.update_state(config, {"approval_status": "reject"}, as_node="human_approval")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: list(graph.stream(None, config=config, stream_mode="updates"))
    )
    return {"thread_id": thread_id, "status": "rejected", "message": "Trip restarted"}

@app.get("/stream/{thread_id}")
async def stream_progress(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    async def event_generator():
        node_labels = {
            "preference_extractor": "Extracting preferences...",
            "destination_researcher": "Researching destination...",
            "weather_fetcher": "Fetching weather forecast...",
            "flights_hotels_searcher": "Searching flights & hotels...",
            "itinerary_generator": "Generating itinerary...",
            "quality_checker": "Checking quality...",
            "human_approval": "Waiting for your approval...",
            "booking_executor": "Confirming bookings...",
        }
        try:
            loop = asyncio.get_event_loop()
            def run_stream():
                events = []
                for event in graph.stream(None, config=config, stream_mode="updates"):
                    events.append(event)
                return events
            events = await loop.run_in_executor(None, run_stream)
            for event in events:
                for node, data in event.items():
                    label = node_labels.get(node, node)
                    payload = {
                        "node": node,
                        "label": label,
                        "quality_score": data.get("quality_score"),
                        "done": True
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.1)
            yield f"data: {json.dumps({'node': 'complete', 'label': 'Done!', 'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/export/{thread_id}")
async def export_pdf(thread_id: str):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import io
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = graph.get_state(config)
    state = snapshot.values
    itinerary = state.get("itinerary", {})
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"Trip to {itinerary.get('destination', 'Unknown')}", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(itinerary.get("summary", ""), styles["Normal"]))
    story.append(Spacer(1, 12))
    for day in itinerary.get("days", []):
        story.append(Paragraph(f"Day {day['day']} - {day['date']}", styles["Heading2"]))
        for period in ["morning", "afternoon", "evening"]:
            act = day.get(period, {})
            story.append(Paragraph(f"{period.capitalize()}: {act.get('name', '')} at {act.get('location', '')} - ${act.get('estimated_cost', 0)}", styles["Normal"]))
        story.append(Paragraph(f"Hotel: {day.get('hotel')} - ${day.get('hotel_cost')}/night", styles["Normal"]))
        story.append(Paragraph(f"Daily Total: ${day.get('daily_total')}", styles["Normal"]))
        story.append(Spacer(1, 8))
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=trip_{thread_id[:8]}.pdf"})
