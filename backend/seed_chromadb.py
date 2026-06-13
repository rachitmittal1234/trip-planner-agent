import httpx
from tools.rag_tool import add_documents

CITIES = ["Paris", "Tokyo", "Bali", "New_York_City", "Dubai", "London", "Rome", "Barcelona", "Bangkok", "Singapore", "Amsterdam", "Istanbul", "Prague", "Sydney", "Mumbai"]

HEADERS = {"User-Agent": "TripPlannerBot/1.0 (educational project)"}

def scrape_wikivoyage(city: str) -> str:
    print(f"  Scraping {city}...")
    try:
        r = httpx.get(
            "https://en.wikivoyage.org/w/api.php",
            params={
                "action": "query",
                "titles": city,
                "prop": "extracts",
                "explaintext": True,
                "format": "json"
            },
            headers=HEADERS,
            timeout=15
        )
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            return ""
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            return page.get("extract", "")
    except Exception as e:
        print(f"    Error: {e}")
    return ""

def chunk_text(text: str, city: str, chunk_size: int = 500) -> list[dict]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        if len(chunk) > 100:
            chunks.append({
                "id": f"{city.lower()}-chunk-{i}",
                "text": chunk,
                "metadata": {"city": city.lower()}
            })
    return chunks

all_docs = []
for city in CITIES:
    text = scrape_wikivoyage(city)
    if text:
        chunks = chunk_text(text, city)
        all_docs.extend(chunks)
        print(f"  ✅ {city}: {len(chunks)} chunks")
    else:
        print(f"  ⚠️  {city}: no data, skipping")

print(f"\nTotal docs to embed: {len(all_docs)}")
if all_docs:
    add_documents(all_docs)
    print("✅ ChromaDB seeded with real Wikivoyage data!")
else:
    print("❌ No data scraped, check your internet connection")
