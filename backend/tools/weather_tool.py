import httpx

def get_weather(destination: str) -> dict:
    print(f">> Fetching weather for: {destination}")

    # Get coordinates using Open-Meteo geocoding
    geo = httpx.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={destination}&count=1"
    ).json()

    if not geo.get("results"):
        return {"error": f"Could not find location: {destination}"}

    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    # Get 7-day forecast
    forecast = httpx.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&timezone=auto&forecast_days=7"
    ).json()

    days = []
    daily = forecast.get("daily", {})
    for i in range(len(daily.get("time", []))):
        days.append({
            "date": daily["time"][i],
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precipitation": daily["precipitation_sum"][i],
        })

    return {
        "destination": destination,
        "lat": lat,
        "lon": lon,
        "forecast": days
    }
