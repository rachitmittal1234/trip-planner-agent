import random
import string
from datetime import datetime
from state import TripState


def _generate_confirmation_code(prefix: str = "") -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{suffix}"


def _parse_price(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        import re
        match = re.search(r"[\d.]+", value)
        if match:
            return float(match.group())
    return 0.0


def booking_executor(state: TripState) -> dict:
    print(">> booking_executor running")

    itinerary = state.get("itinerary", {})
    source = state.get("source", "Origin")
    destination = state.get("destination", "Unknown")
    dates = state.get("dates", "Unknown")

    flight_options = state.get("flight_options", {})
    if isinstance(flight_options, dict):
        raw_flights = flight_options.get("flights", [])
    elif isinstance(flight_options, list):
        raw_flights = flight_options
    else:
        raw_flights = []

    flights = []
    if raw_flights:
        chosen = raw_flights[0]
        flights.append({
            "confirmation_code": _generate_confirmation_code("FL"),
            "airline": chosen.get("airline", "Amadeus Airways"),
            "from": chosen.get("from", source),
            "to": chosen.get("to", destination),
            "departure": chosen.get("departure", dates.split(" to ")[0] if " to " in dates else dates),
            "arrival": chosen.get("arrival", ""),
            "duration": chosen.get("duration", ""),
            "stops": chosen.get("stops", 0),
            "price_usd": _parse_price(chosen.get("price", 450)),
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat() + "Z",
        })
    else:
        flights.append({
            "confirmation_code": _generate_confirmation_code("FL"),
            "airline": "Amadeus Airways (Sandbox)",
            "from": source,
            "to": destination,
            "departure": dates.split(" to ")[0] if " to " in dates else dates,
            "arrival": dates.split(" to ")[-1] if " to " in dates else dates,
            "duration": "N/A",
            "stops": 0,
            "price_usd": round(random.uniform(300, 800), 2),
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat() + "Z",
        })

    hotel_options = state.get("hotel_options", {})
    if isinstance(hotel_options, dict):
        raw_hotels = hotel_options.get("hotels", [])
    elif isinstance(hotel_options, list):
        raw_hotels = hotel_options
    else:
        raw_hotels = []

    days = itinerary.get("days", [])
    num_nights = len(days) if days else 1

    hotels = []
    if raw_hotels:
        chosen = raw_hotels[0]
        price_per_night = _parse_price(chosen.get("price_per_night", 120))
        hotels.append({
            "confirmation_code": _generate_confirmation_code("HT"),
            "hotel_name": chosen.get("name", "Grand Hotel"),
            "location": chosen.get("location", destination),
            "check_in": dates.split(" to ")[0] if " to " in dates else dates,
            "check_out": dates.split(" to ")[-1] if " to " in dates else dates,
            "nights": num_nights,
            "price_per_night_usd": price_per_night,
            "total_usd": round(price_per_night * num_nights, 2),
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat() + "Z",
        })
    else:
        price_per_night = round(random.uniform(80, 200), 2)
        hotels.append({
            "confirmation_code": _generate_confirmation_code("HT"),
            "hotel_name": f"{destination} Grand Hotel (Sandbox)",
            "location": destination,
            "check_in": dates.split(" to ")[0] if " to " in dates else dates,
            "check_out": dates.split(" to ")[-1] if " to " in dates else dates,
            "nights": num_nights,
            "price_per_night_usd": price_per_night,
            "total_usd": round(price_per_night * num_nights, 2),
            "status": "CONFIRMED",
            "booked_at": datetime.utcnow().isoformat() + "Z",
        })

    total_flight_cost = sum(f["price_usd"] for f in flights)
    total_hotel_cost = sum(h["total_usd"] for h in hotels)
    itinerary_cost = _parse_price(itinerary.get("total_estimated_cost", 0))

    booking_confirmation = {
        "booking_id": _generate_confirmation_code("TRIP"),
        "status": "ALL_CONFIRMED",
        "source": source,
        "destination": destination,
        "dates": dates,
        "flights": flights,
        "hotels": hotels,
        "cost_breakdown": {
            "flights_usd": round(total_flight_cost, 2),
            "hotels_usd": round(total_hotel_cost, 2),
            "activities_usd": round(itinerary_cost, 2),
            "total_usd": round(total_flight_cost + total_hotel_cost + itinerary_cost, 2),
        },
        "confirmed_at": datetime.utcnow().isoformat() + "Z",
        "note": "This is a sandbox booking. No real charges were made.",
    }

    print(f"   ✅ Booking confirmed: {booking_confirmation['booking_id']}")
    print(f"   ✈️  Flight: {flights[0]['confirmation_code']} ({source} → {destination})")
    print(f"   🏨 Hotel: {hotels[0]['confirmation_code']}")

    return {"booking_confirmation": booking_confirmation}
