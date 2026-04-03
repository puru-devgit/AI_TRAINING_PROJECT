from database import engine
from sqlalchemy import text
import requests

# 1. DB connection
conn = engine.connect()
print("PostgreSQL connected")

# 2. Tables
tables = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
print(f"Tables found: {[t[0] for t in tables]}")
conn.close()

# 3. API endpoints
base = "http://localhost:8000"
for ep in ["/", "/inventory/", "/orders/"]:
    try:
        r = requests.get(base + ep, timeout=5)
        print(f"OK GET {ep} -> {r.status_code}")
    except Exception as e:
        print(f"FAIL GET {ep} -> {e}")
