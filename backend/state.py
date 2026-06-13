from typing import TypedDict, Optional, List, Any, Annotated
import operator

def keep_last(a, b):
    return b if b is not None else a

def keep_first(a, b):
    # Keep a only if it's a non-empty, non-None value
    if a is not None and a != "" and a != []:
        return a
    return b

class TripState(TypedDict):
    source: Annotated[str, keep_first]
    destination: Annotated[str, keep_first]
    dates: Annotated[str, keep_first]
    budget: Annotated[str, keep_first]
    travel_style: Annotated[str, keep_first]
    preferences: Annotated[List[str], keep_first]
    research_results: Annotated[Optional[Any], keep_last]
    weather_data: Annotated[Optional[Any], keep_last]
    flight_options: Annotated[Optional[Any], keep_last]
    hotel_options: Annotated[Optional[Any], keep_last]
    itinerary: Annotated[Optional[Any], keep_last]
    quality_score: Annotated[Optional[float], keep_last]
    approval_status: Annotated[Optional[str], keep_last]
    booking_confirmation: Annotated[Optional[Any], keep_last]
    error: Annotated[Optional[str], keep_last]
    parallel_done: Annotated[List[str], operator.add]
    retry_count: Annotated[Optional[int], keep_last]
