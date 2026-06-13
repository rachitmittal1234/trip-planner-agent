import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from state import TripState

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def itinerary_generator(state: TripState) -> dict:
    print(">> itinerary_generator running")

    destination = state.get("destination", "")
    dates = state.get("dates", "")
    budget = state.get("budget", "0")
    travel_style = state.get("travel_style", "balanced")
    preferences = state.get("preferences", [])
    retry_count = state.get("retry_count", 0)

    print(f"   destination={destination}, dates={dates}, budget={budget}")

    research = state.get("research_results") or {}
    weather = state.get("weather_data") or {}
    flights = state.get("flight_options") or []
    hotels = state.get("hotel_options") or []

    web_snippets = "\n".join([r["content"][:200] for r in research.get("web", [])])
    rag_snippets = "\n".join(research.get("rag", []))

    weather_summary = "\n".join([
        f"{d['date']}: {d['temp_max']}°C max, {d['temp_min']}°C min, {d['precipitation']}mm rain"
        for d in weather.get("forecast", [])
    ]) if weather.get("forecast") else "Weather data unavailable."

    flights_summary = "\n".join([
        f"{f['airline']} — ${f['price']} — {f['stops']} stops"
        for f in flights
    ]) if flights else "No flight data."

    hotels_summary = "\n".join([
        f"{h['name']} ({h['stars']}★) — ${h['price_per_night']}/night — Rating: {h['rating']}"
        for h in hotels
    ]) if hotels else "No hotel data."

    feedback_section = ""
    if retry_count > 0:
        feedback_section = f"""
IMPORTANT — USER REQUESTED CHANGES TO THE PREVIOUS ITINERARY:
"{state.get("error", "Improve budget fit and logical travel distances.")}"

You MUST incorporate this request into the new itinerary. If the user asked to
add, remove, or replace a location/activity/destination, restructure the days
accordingly (e.g. allocate specific days to the newly requested place, adjust
travel logistics, and update costs). Do not simply produce a similar itinerary
without reflecting this requested change.
"""

    # Calculate number of days from dates
    try:
        from datetime import datetime
        parts = dates.split(" to ")
        start = datetime.strptime(parts[0].strip(), "%Y-%m-%d")
        end = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
        num_days = (end - start).days
    except Exception:
        num_days = 3

    prompt = f"""
You are an expert travel planner. Create a detailed day-by-day itinerary as valid JSON only.
No markdown, no explanation — just raw JSON.

DESTINATION: {destination}
DATES: {dates}
NUMBER OF DAYS: {num_days}
BUDGET: ${budget} USD total
TRAVEL STYLE: {travel_style}
PREFERENCES: {', '.join(preferences)}

WEATHER FORECAST:
{weather_summary}

RESEARCH:
{web_snippets}
{rag_snippets}

FLIGHT OPTIONS:
{flights_summary}

HOTEL OPTIONS:
{hotels_summary}

{feedback_section}

IMPORTANT RULES:
- Create exactly {num_days} days in the itinerary
- Total cost must stay within ${budget} USD
- Use actual dates starting from {dates.split(' to ')[0] if ' to ' in dates else dates}

Return ONLY this JSON structure:
{{
  "destination": "{destination}",
  "total_days": {num_days},
  "total_estimated_cost": 1200.0,
  "currency": "USD",
  "summary": "2-3 sentence trip summary",
  "packing_tips": ["tip1", "tip2", "tip3", "tip4", "tip5"],
  "recommended_flight": "airline name and price",
  "recommended_hotel": "hotel name and price per night",
  "days": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "morning": {{
        "time": "9:00 AM",
        "name": "Activity name",
        "description": "Brief description",
        "location": "Address or area",
        "estimated_cost": 20.0,
        "duration_minutes": 90
      }},
      "afternoon": {{ same structure }},
      "evening": {{ same structure }},
      "hotel": "Hotel name",
      "hotel_cost": 120.0,
      "daily_total": 250.0,
      "notes": "Tips for the day"
    }}
  ]
}}
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        itinerary = json.loads(raw)
    except json.JSONDecodeError:
        itinerary = {"raw": raw, "parse_error": True}

    return {"itinerary": itinerary, "retry_count": retry_count}
