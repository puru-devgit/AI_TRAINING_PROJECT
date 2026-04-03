from database import engine, SessionLocal
from models import Base, Product, Inventory, SalesHistory, Supplier, PurchaseOrder
import random
import math
from datetime import date, timedelta


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Product).count() > 0:
        print("Database already seeded.")
        db.close()
        return

    # --- Products ---
    products = [
        Product(name="Rice",        category="Grains",    unit="kg",    reorder_point=80,  lead_time_days=4, holding_cost=0.5,  order_cost=40),
        Product(name="Wheat Flour", category="Grains",    unit="kg",    reorder_point=60,  lead_time_days=3, holding_cost=0.4,  order_cost=35),
        Product(name="Sugar",       category="Sweetener", unit="kg",    reorder_point=50,  lead_time_days=5, holding_cost=0.6,  order_cost=45),
        Product(name="Coffee Beans",category="Beverages", unit="kg",    reorder_point=30,  lead_time_days=7, holding_cost=2.0,  order_cost=80),
        Product(name="Cooking Oil", category="Oils",      unit="litre", reorder_point=40,  lead_time_days=4, holding_cost=1.2,  order_cost=55),
    ]
    db.add_all(products)
    db.flush()

    # --- Inventory (simulate imminent stockout for Rice) ---
    stocks = [15, 90, 20, 55, 70]
    for p, s in zip(products, stocks):
        db.add(Inventory(product_id=p.id, stock=s))

    # --- Suppliers ---
    suppliers_data = [
        ("AgriSupply Co",   1, 12.0, 4, 0.92),
        ("GrainMart",       1, 10.5, 6, 0.78),
        ("FlourWorld",      2, 8.0,  3, 0.95),
        ("SweetSource",     3, 5.5,  5, 0.85),
        ("BeanOrigin",      4, 45.0, 7, 0.90),
        ("OilDepot",        5, 18.0, 4, 0.88),
    ]
    suppliers = []
    for name, pid, price, lt, rel in suppliers_data:
        s = Supplier(name=name, product_id=pid, price_per_unit=price, lead_time_days=lt, reliability_score=rel)
        db.add(s)
        suppliers.append(s)

    # --- Sales History (365 days with seasonality + noise) ---
    start = date.today() - timedelta(days=365)
    for p_idx, p in enumerate(products):
        base_demand = [30, 22, 18, 10, 15][p_idx]
        for i in range(365):
            d = start + timedelta(days=i)
            # seasonal wave + weekly pattern + noise
            seasonal = math.sin(2 * math.pi * i / 365) * base_demand * 0.4
            weekly   = math.sin(2 * math.pi * d.weekday() / 7) * base_demand * 0.15
            qty = max(1, base_demand + seasonal + weekly + random.gauss(0, base_demand * 0.1))
            db.add(SalesHistory(product_id=p.id, sale_date=d, quantity_sold=round(qty, 2)))

    db.commit()
    db.close()
    print("✅ Database seeded successfully.")


if __name__ == "__main__":
    seed()
