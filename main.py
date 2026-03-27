from fastapi import FastAPI

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="supply_chain",
    user="postgres",
    password="Puru@2107"
)

cursor = conn.cursor()

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/test")
def test():
    return {"status": "working"}

@app.get("/inventory")
def get_inventory():
    cursor.execute("SELECT * FROM inventory")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "product_name": row[1],
            "quantity": row[2]
        })

    return {"inventory": result}

@app.get("/forecast")
def get_forecast():
    forecast = [100, 120, 140, 130]
    return {"forecast": forecast}

@app.get("/forecast/{product_id}")
def forecast_product(product_id: int):
    cursor.execute("SELECT * FROM inventory WHERE id=%s", (product_id,))
    product = cursor.fetchone()

    return {
        "product": {
            "id": product[0],
            "name": product[1],
            "current_stock": product[2]
        },
        "forecast": [60, 70, 80]
    }