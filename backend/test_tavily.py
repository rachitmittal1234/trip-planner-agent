from tools.search_tool import search_destination

result = search_destination("Paris")
print(f"✅ Got {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['title']}")
