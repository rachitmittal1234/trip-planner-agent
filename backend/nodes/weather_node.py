from state import TripState
from tools.weather_tool import get_weather

def weather_fetcher(state: TripState) -> dict:
    print(f">> weather_fetcher running")
    destination = state["destination"]
    print(f">> Fetching weather for: {destination}")
    return {
        "weather_data": get_weather(destination),
        "parallel_done": ["weather"],
    }
