import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_destination(destination: str) -> dict:
    print(f">> Searching web for: {destination}")
    
    results = client.search(
        query=f"{destination} travel guide things to do attractions tips",
        max_results=5
    )
    
    return {
        "query": destination,
        "results": [
            {
                "title": r["title"],
                "content": r["content"],
                "url": r["url"]
            }
            for r in results.get("results", [])
        ]
    }
