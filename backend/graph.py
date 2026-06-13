import sqlite3
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from langgraph.checkpoint.sqlite import SqliteSaver
from state import TripState
from nodes.preference_node import preference_extractor
from nodes.research_node import destination_researcher
from nodes.weather_node import weather_fetcher
from nodes.flights_node import flights_hotels_searcher
from nodes.itinerary_node import itinerary_generator
from nodes.quality_node import quality_checker
from nodes.booking_node import booking_executor

def human_approval(state: TripState) -> TripState:
    print(">> human_approval running")
    state["approval_status"] = "approve"
    return state

def should_retry_quality(state: TripState) -> str:
    if state.get("quality_score", 0) < 0.7:
        return "retry"
    return "done"

def approval_branch(state: TripState) -> str:
    return state.get("approval_status", "reject")

def fan_out(state: TripState) -> list:
    print(">> fanning out to parallel research nodes")
    return [
        Send("destination_researcher", state),
        Send("weather_fetcher", state),
        Send("flights_hotels_searcher", state),
    ]

def fan_in(state: TripState) -> str:
    done = state.get("parallel_done", [])
    print(f">> fan_in: completed {done}")
    if len(done) >= 3:
        return "itinerary_generator"
    return "fan_in_wait"

builder = StateGraph(TripState)

builder.add_node("preference_extractor", preference_extractor)
builder.add_node("destination_researcher", destination_researcher)
builder.add_node("weather_fetcher", weather_fetcher)
builder.add_node("flights_hotels_searcher", flights_hotels_searcher)
builder.add_node("itinerary_generator", itinerary_generator)
builder.add_node("quality_checker", quality_checker)
builder.add_node("human_approval", human_approval)
builder.add_node("booking_executor", booking_executor)

builder.set_entry_point("preference_extractor")
builder.add_conditional_edges("preference_extractor", fan_out, ["destination_researcher", "weather_fetcher", "flights_hotels_searcher"])
builder.add_edge("destination_researcher", "itinerary_generator")
builder.add_edge("weather_fetcher", "itinerary_generator")
builder.add_edge("flights_hotels_searcher", "itinerary_generator")
builder.add_edge("itinerary_generator", "quality_checker")

builder.add_conditional_edges("quality_checker", should_retry_quality, {
    "retry": "itinerary_generator",
    "done": "human_approval"
})

builder.add_conditional_edges("human_approval", approval_branch, {
    "approve": "booking_executor",
    "edit": "itinerary_generator",
    "reject": "preference_extractor"
})

builder.add_edge("booking_executor", END)

conn = sqlite3.connect("trip_planner.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = builder.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])
