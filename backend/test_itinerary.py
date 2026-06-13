from nodes.research_node import destination_researcher
from nodes.weather_node import weather_fetcher
from nodes.flights_node import flights_hotels_searcher
from nodes.itinerary_node import itinerary_generator

state = {
    "destination": "Paris",
    "dates": "2025-07-01 to 2025-07-07",
    "budget": "2000 USD",
    "travel_style": "leisure",
    "preferences": ["museums", "food", "history"],
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

state = destination_researcher(state)
state = weather_fetcher(state)
state = flights_hotels_searcher(state)
state = itinerary_generator(state)

print("\n✅ ITINERARY GENERATED!")
print("="*50)
print(state["itinerary"][:1000])
print("="*50)
