from nodes.weather_node import weather_fetcher

state = {"destination": "Paris", "dates": None, "budget": None, "travel_style": None, "preferences": [], "research_results": None, "weather_data": None, "flight_options": None, "hotel_options": None, "itinerary": None, "quality_score": None, "approval_status": None, "booking_confirmation": None, "error": None}

result = weather_fetcher(state)
forecast = result["weather_data"]["forecast"]
print(f"✅ Got {len(forecast)} forecast entries for Paris")
print(f"  First entry: {forecast[0]['date']} — {forecast[0]['temp_max']}°C")
