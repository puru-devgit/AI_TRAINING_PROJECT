import requests

BASE_URL = "http://localhost:8000"

def get_inventory():
    try:
        res = requests.get(f"{BASE_URL}/inventory")
        return res.json()
    except:
        return []

def get_forecast():
    try:
        res = requests.get(f"{BASE_URL}/forecast")
        return res.json()
    except:
        return []

def get_sales():
    try:
        res = requests.get(f"{BASE_URL}/sales")
        return res.json()
    except:
        return []

def ask_agent(query):
    try:
        res = requests.post(
            f"{BASE_URL}/agent",
            json={"query": query}
        )
        return res.json()
    except:
        return {"response": "⚠️ Backend not connected"}