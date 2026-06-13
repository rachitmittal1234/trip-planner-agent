from state import TripState
from tools.search_tool import search_destination
from tools.rag_tool import query_rag

def destination_researcher(state: TripState) -> dict:
    destination = state["destination"]
    print(f">> destination_researcher running for: {destination}")
    web_results = search_destination(destination)
    rag_results = query_rag(destination)
    return {
        "research_results": {"web": web_results["results"], "rag": rag_results},
        "parallel_done": ["research"],
    }
