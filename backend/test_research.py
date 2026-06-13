from nodes.research_node import destination_researcher

state = {
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

result = destination_researcher(state)
print(f"\n✅ Web results: {len(result['research_results']['web'])}")
print(f"✅ RAG results: {len(result['research_results']['rag'])}")
