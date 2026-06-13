import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from state import TripState

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

MAX_RETRIES = 2

def quality_checker(state: TripState) -> dict:
    print(">> quality_checker running")

    itinerary = state.get("itinerary", {})
    retry_count = state.get("retry_count", 0)

    if itinerary.get("parse_error"):
        print("   ❌ Itinerary JSON parse error")
        return {
            "quality_score": 0.0,
            "retry_count": retry_count + 1,
            "error": "Itinerary was not valid JSON. Return only raw JSON with no markdown."
        }

    if retry_count >= MAX_RETRIES:
        print(f"   ⚠️  Max retries ({MAX_RETRIES}) reached — passing itinerary through")
        return {"quality_score": 0.7}

    prompt = f"""
You are a travel plan quality reviewer. Review this itinerary and score it.

TRIP CONTEXT:
- Destination: {state.get('destination')}
- Dates: {state.get('dates')}
- Total Budget: ${state.get('budget')} USD
- Travel Style: {state.get('travel_style', 'balanced')}

ITINERARY TO REVIEW:
{json.dumps(itinerary, indent=2)}

Evaluate on these criteria:
1. Budget fit — does total_estimated_cost stay within ${state.get('budget')} USD?
2. Logical distances — are morning/afternoon/evening activities geographically sensible?
3. Date feasibility — do the dates match the requested travel dates?
4. Completeness — are all days fully planned with costs?
5. Weather alignment — do activities suit the weather?

Respond ONLY with this JSON (no markdown, no explanation):
{{
  "score": 0.85,
  "passed": true,
  "feedback": "Brief feedback if score < 0.7, else empty string"
}}
Score 0.0 to 1.0. Use 0.7 as the passing threshold.
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        result = json.loads(raw)
        score = float(result.get("score", 0.5))
        feedback = result.get("feedback", "")
    except (json.JSONDecodeError, ValueError):
        score = 0.5
        feedback = "Quality check response was malformed. Try again."

    print(f"   Quality score: {score}")
    new_retry = retry_count + 1 if score < 0.7 else retry_count

    return {
        "quality_score": score,
        "retry_count": new_retry,
        "error": feedback if score < 0.7 else "",
    }
