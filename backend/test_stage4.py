import json
from graph import graph

test_state = {
    "destination": "Paris",
    "dates": "2025-08-01 to 2025-08-05",
    "budget": "2000",
    "travel_style": "cultural",
    "preferences": ["museums", "local food", "walking tours"],
    "research_results": {
        "web": [{"content": "Paris is known for the Eiffel Tower, Louvre Museum, and amazing cafes. Best visited in summer."}],
        "rag": ["Paris has excellent metro connectivity. Avoid tourist traps near major landmarks."]
    },
    "weather_data": {
        "forecast": [
            {"date": "2025-08-01", "temp_max": 28, "temp_min": 18, "precipitation": 0},
            {"date": "2025-08-02", "temp_max": 30, "temp_min": 20, "precipitation": 2},
            {"date": "2025-08-03", "temp_max": 27, "temp_min": 17, "precipitation": 0},
            {"date": "2025-08-04", "temp_max": 25, "temp_min": 16, "precipitation": 5},
            {"date": "2025-08-05", "temp_max": 26, "temp_min": 17, "precipitation": 0}
        ]
    },
    "flight_options": [
        {"airline": "Air France", "price": "$450", "stops": 0},
        {"airline": "British Airways", "price": "$380", "stops": 1}
    ],
    "hotel_options": [
        {"name": "Hotel Le Marais", "stars": 4, "price_per_night": "$180", "rating": 8.7},
        {"name": "Ibis Paris Centre", "stars": 3, "price_per_night": "$110", "rating": 7.9}
    ],
    "parallel_done": ["destination_researcher", "weather_fetcher", "flights_hotels_searcher"],
    "retry_count": 0
}

config = {"configurable": {"thread_id": "test-stage4-001"}}

print("�� Running Stage 4 test (itinerary_generator → quality_checker)...\n")

for event in graph.stream(test_state, config=config, stream_mode="updates"):
    for node, data in event.items():
        print(f"✅ Node: {node}")
        if node == "quality_checker":
            print(f"   Quality Score: {data.get('quality_score')}")
            print(f"   Retry Count:   {data.get('retry_count')}")
        if node == "itinerary_generator":
            itin = data.get("itinerary", {})
            if isinstance(itin, dict) and not itin.get("parse_error"):
                print(f"   Destination:   {itin.get('destination')}")
                print(f"   Total Days:    {itin.get('total_days')}")
                print(f"   Est. Cost:     ${itin.get('total_estimated_cost')}")
            else:
                print("   ⚠️  Itinerary parse issue")
        print()

# Check final state
snapshot = graph.get_state(config)
final = snapshot.values
print("=" * 50)
print(f"Final quality_score : {final.get('quality_score')}")
print(f"Final retry_count   : {final.get('retry_count')}")
print(f"Approval status     : {final.get('approval_status', 'pending (graph paused)')}")
print(f"Next node           : {snapshot.next}")

itin = final.get("itinerary", {})
if isinstance(itin, dict) and "days" in itin:
    print(f"\n📅 Itinerary has {len(itin['days'])} days planned")
    print(f"📝 Summary: {itin.get('summary', '')[:150]}")
