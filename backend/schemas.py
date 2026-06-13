from pydantic import BaseModel, Field
from typing import List, Optional

class Activity(BaseModel):
    time: str = Field(description="Time of activity e.g. '9:00 AM'")
    name: str = Field(description="Name of the activity")
    description: str = Field(description="Brief description")
    location: str = Field(description="Location/address")
    estimated_cost: float = Field(description="Cost in USD")
    duration_minutes: int = Field(description="Duration in minutes")

class DayPlan(BaseModel):
    day: int = Field(description="Day number starting from 1")
    date: str = Field(description="Date in YYYY-MM-DD format")
    morning: Activity
    afternoon: Activity
    evening: Activity
    hotel: str = Field(description="Hotel name for the night")
    hotel_cost: float = Field(description="Hotel cost per night in USD")
    daily_total: float = Field(description="Total cost for the day in USD")
    notes: str = Field(description="Any special notes or tips for the day")

class TripPlan(BaseModel):
    destination: str
    total_days: int
    total_estimated_cost: float
    currency: str = "USD"
    days: List[DayPlan]
    summary: str = Field(description="2-3 sentence trip summary")
    packing_tips: List[str] = Field(description="5 packing tips for this destination")
