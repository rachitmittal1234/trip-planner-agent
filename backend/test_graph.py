from graph import graph

dummy_state = {
    "destination": "Paris",
    "dates": "2025-06-01 to 2025-06-07",
    "budget": "2000 USD",
    "travel_style": "leisure",
    "preferences": ["museums", "food"],
    "research_results": None,
    "weather_data": None,
    "flight_options": None,
    "hotel_options": None,
    "itinerary": None,
    "quality_score": None,
    "approval_status": None,
    "booking_confirmation": None,
    "error": None
}

config = {"configurable": {"thread_id": "test-1"}}
result = graph.invoke(dummy_state, config=config)
print("\n✅ Graph ran successfully!")
print("Quality score:", result.get("quality_score"))
