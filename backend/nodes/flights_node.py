from state import TripState

def flights_hotels_searcher(state: TripState) -> dict:
    print(f">> flights_hotels_searcher running")
    source = state.get("source", "Origin")
    destination = state.get("destination", "Destination")
    return {
        "flight_options": [
            {"airline": "Air France", "from": source, "to": destination, "departure": "09:00", "arrival": "14:30", "duration": "5h 30m", "price": 450, "stops": 0},
            {"airline": "Emirates", "from": source, "to": destination, "departure": "14:00", "arrival": "22:00", "duration": "8h 00m", "price": 320, "stops": 1},
            {"airline": "Lufthansa", "from": source, "to": destination, "departure": "06:00", "arrival": "11:00", "duration": "5h 00m", "price": 510, "stops": 0},
        ],
        "hotel_options": [
            {"name": f"Grand Hotel {destination}", "stars": 4, "price_per_night": 120, "location": "City Center", "rating": 8.5},
            {"name": f"{destination} Budget Inn", "stars": 3, "price_per_night": 65, "location": "Near Metro", "rating": 7.8},
            {"name": f"Luxury Suites {destination}", "stars": 5, "price_per_night": 280, "location": "Downtown", "rating": 9.2},
        ],
        "parallel_done": ["flights"],
    }
