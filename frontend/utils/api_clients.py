import requests

BASE = "http://localhost:8000"


def _get(path, params=None):
    try:
        r = requests.get(f"{BASE}{path}", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _post(path, payload):
    try:
        r = requests.post(f"{BASE}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_inventory():
    return _get("/inventory/")


def update_stock(product_id: int, stock: float):
    return _get(f"/inventory/{product_id}/stock", params={"stock": stock})


def get_forecast(product_id: int = 1, periods: int = 30):
    return _get("/forecast/", params={"product_id": product_id, "periods": periods})


def get_sales_history(product_id: int = 1):
    return _get("/forecast/sales", params={"product_id": product_id})


def get_orders():
    return _get("/orders/")


def get_weather(city: str = "Mumbai"):
    return _get("/weather/", params={"city": city})


def ask_agent(query: str):
    return _post("/agent/", {"query": query})


def get_risks(query: str = "supply chain disruption", top_k: int = 5):
    return _get("/risks/", params={"query": query, "top_k": top_k})
