import pandas as pd
import numpy as np
from datetime import date, timedelta
import math
import random
from database import engine, SessionLocal
from models import Base, Product, Inventory, SalesHistory, Supplier, PurchaseOrder
from sqlalchemy import text

random.seed(42)
np.random.seed(42)

db = SessionLocal()

# Drop and recreate tables
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    conn.commit()
Base.metadata.create_all(bind=engine)
print("Tables recreated")

# --- 1. Products (10 retail items across categories) ---
products_data = [
    ("Rice (Basmati 5kg)",     "Grains",      "kg",     120, 5, 0.8,  60),
    ("Wheat Flour (10kg)",     "Grains",      "kg",     80,  4, 0.5,  45),
    ("Sugar (2kg)",            "Sweeteners",  "kg",     100, 3, 0.6,  40),
    ("Cooking Oil (5L)",       "Oils",        "litre",  60,  4, 1.2,  55),
    ("Coffee Beans (1kg)",     "Beverages",   "kg",     40,  7, 2.5,  80),
    ("Black Tea (500g)",       "Beverages",   "pack",   50,  5, 1.0,  50),
    ("Lentils (1kg)",          "Pulses",      "kg",     90,  4, 0.7,  45),
    ("Tomato Paste (400g)",    "Canned",      "can",    70,  3, 0.4,  35),
    ("Pasta (500g)",           "Grains",      "pack",   85,  4, 0.5,  40),
    ("Olive Oil (1L)",         "Oils",        "litre",  35,  6, 2.0,  70),
]

products = []
for name, cat, unit, rop, lt, hc, oc in products_data:
    p = Product(name=name, category=cat, unit=unit, reorder_point=rop,
                lead_time_days=lt, holding_cost=hc, order_cost=oc)
    db.add(p)
    products.append(p)
db.flush()
print(f"Loaded {len(products)} products")

# --- 2. Inventory (varied stock levels — some critical, some healthy) ---
stock_levels = [95, 200, 45, 150, 38, 120, 80, 200, 170, 30]
for p, stock in zip(products, stock_levels):
    db.add(Inventory(product_id=p.id, stock=stock))
db.commit()
print("Loaded inventory")

# --- 3. Suppliers (2 per product) ---
supplier_names = [
    ("AgriSupply Co",     0.92), ("GrainMart Ltd",      0.78),
    ("FlourWorld",        0.95), ("BestGrain Inc",      0.82),
    ("SweetSource",       0.88), ("SugarKing",          0.75),
    ("OilDepot",          0.90), ("PureOils Ltd",       0.85),
    ("BeanOrigin",        0.93), ("CoffeeDirect",       0.80),
    ("TeaHouse Exports",  0.87), ("LeafSupply",         0.79),
    ("PulseWorld",        0.91), ("LentilFarm Co",      0.83),
    ("CanCo Supplies",    0.86), ("TomatoFresh",        0.77),
    ("PastaItalia",       0.94), ("NoodleCraft",        0.81),
    ("MedOil Imports",    0.89), ("OliveGrove Co",      0.84),
]
base_prices = [12.0, 8.0, 5.5, 18.0, 45.0, 9.0, 6.5, 3.5, 4.0, 28.0]

suppliers = []
for i, p in enumerate(products):
    for j in range(2):
        idx = i * 2 + j
        name, rel = supplier_names[idx]
        price = base_prices[i] * (1 + j * 0.1)
        lt = p.lead_time_days + j
        s = Supplier(name=name, product_id=p.id, price_per_unit=round(price, 2),
                     lead_time_days=lt, reliability_score=rel)
        db.add(s)
        suppliers.append(s)
db.commit()
print(f"Loaded {len(suppliers)} suppliers")

# --- 4. Sales History (5 years daily — strong seasonality for Prophet) ---
start = date(2019, 1, 1)
end = date(2023, 12, 31)
days = (end - start).days + 1

base_demands = [35, 28, 22, 18, 12, 15, 25, 20, 30, 8]

count = 0
for p_idx, p in enumerate(products):
    base = base_demands[p_idx]
    for i in range(days):
        d = start + timedelta(days=i)
        day_of_year = d.timetuple().tm_yday

        # Yearly seasonality (peak in winter/festive)
        yearly = math.sin(2 * math.pi * (day_of_year - 80) / 365) * base * 0.35

        # Weekly seasonality (peak on weekends)
        weekly = math.sin(2 * math.pi * d.weekday() / 7) * base * 0.15

        # Festive spikes (Dec, Ramadan ~Apr, Diwali ~Oct)
        festive = 0
        if d.month == 12:
            festive = base * 0.4
        elif d.month in [4, 10]:
            festive = base * 0.2

        # Random noise
        noise = np.random.normal(0, base * 0.08)

        qty = max(1, round(base + yearly + weekly + festive + noise, 2))
        db.add(SalesHistory(product_id=p.id, sale_date=d, quantity_sold=qty))
        count += 1

    if count % 10000 == 0:
        db.commit()

db.commit()
print(f"Loaded {count} sales records (5 years daily)")

# --- 5. Purchase Orders (realistic history) ---
po_count = 0
for p_idx, p in enumerate(products):
    base = base_demands[p_idx]
    avg_daily = base
    annual = avg_daily * 365
    eoq = round(math.sqrt((2 * annual * p.order_cost) / p.holding_cost), 0)

    # One PO every ~45 days over 5 years
    sup = [s for s in suppliers if s.product_id == p.id]
    for i in range(0, days, 45):
        d = start + timedelta(days=i)
        best = sup[i % 2]
        status = "Delivered" if d < date(2023, 10, 1) else ("In Transit" if d < date(2023, 12, 1) else "Draft")
        db.add(PurchaseOrder(
            product_id=p.id,
            supplier_id=best.id,
            quantity=eoq,
            status=status,
            reason=f"Scheduled replenishment — EOQ={eoq} {p.unit}",
        ))
        po_count += 1

db.commit()
print(f"Loaded {po_count} purchase orders")
db.close()
print("\nAll data generated and loaded successfully!")
print("\nSummary:")
print(f"  Products   : {len(products)}")
print(f"  Suppliers  : {len(suppliers)}")
print(f"  Sales rows : {count} (5 years daily x 10 products)")
print(f"  POs        : {po_count}")
