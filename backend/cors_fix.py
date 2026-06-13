import re

with open('main.py', 'r') as f:
    content = f.read()

old = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

new = '''app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)'''

content = content.replace(old, new)

with open('main.py', 'w') as f:
    f.write(content)

print("Done")
