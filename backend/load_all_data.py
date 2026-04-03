import pandas as pd
import numpy as np
import math
import random
from datetime import date, timedelta
from database import engine, SessionLocal
from models import Base, Product, Inventory, SalesHistory, Supplier, PurchaseOrder
from sqlalchemy import text

random.seed(42)
np.random.seed(42)

db = SessionLocal()

# Reset DB
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    conn.commit()
Base.metadata.create_all(bind=engine)
print("Tables recreated")

products = []
suppliers = []

# ── 1. SUPPLY CHAIN DATA (supply_chain_data.csv) ──────────────────────────────
sc = pd.read_csv("data/supply_chain_data.csv")
sc = sc.drop_duplicates(subset=["SKU"]).head(30)

for _, row in sc.iterrows():
    p = Product(
        name=f"{str(row['Product type']).title()} - {row['SKU']}",
        category=str(row["Product type"]).title(),
        unit="units",
        reorder_point=round(float(row["Stock levels"]) * 0.3, 1),
        lead_time_days=int(row["Lead times"]),
        holding_cost=round(float(row["Manufacturing costs"]) * 0.02, 2),
        order_cost=round(float(row["Shipping costs"]) + 20, 2),
    )
    db.add(p)
    products.append((p, float(row["Stock levels"]), row))

db.flush()

for p, stock, row in products[:30]:
    db.add(Inventory(product_id=p.id, stock=stock))

    s = Supplier(
        name=str(row["Supplier name"]),
        product_id=p.id,
        price_per_unit=round(float(row["Manufacturing costs"]), 2),
        lead_time_days=int(row["Manufacturing lead time"]),
        reliability_score=round(1 - float(row["Defect rates"]), 2),
    )
    db.add(s)
    suppliers.append(s)

db.commit()
print(f"Loaded {len(products)} products from supply_chain_data.csv")

# ── 2. ALCOHOL / BEVERAGE PRODUCTS (BegInvFINAL12312016.csv) ──────────────────
beg = pd.read_csv("data/BegInvFINAL12312016.csv").drop_duplicates(subset=["Brand", "Description"]).head(30)
prices_df = pd.read_csv("data/2017PurchasePricesDec.csv")
prices_map = {str(r["Description"])[:100]: r for _, r in prices_df.iterrows()}

alc_products = []
for _, row in beg.iterrows():
    name = str(row["Description"])[:80]
    p = Product(
        name=name,
        category="Beverages",
        unit="bottles",
        reorder_point=round(float(row["onHand"]) * 0.3, 1),
        lead_time_days=5,
        holding_cost=round(float(row["Price"]) * 0.02, 2),
        order_cost=50.0,
    )
    db.add(p)
    alc_products.append((p, float(row["onHand"]), row))

db.flush()

for p, stock, row in alc_products:
    db.add(Inventory(product_id=p.id, stock=stock))
    pr = prices_map.get(str(row["Description"])[:100])
    vendor = str(pr["VendorName"]) if pr is not None else "Unknown Vendor"
    price = float(pr["PurchasePrice"]) if pr is not None else float(row["Price"]) * 0.7
    s = Supplier(
        name=vendor[:100],
        product_id=p.id,
        price_per_unit=round(price, 2),
        lead_time_days=5,
        reliability_score=0.85,
    )
    db.add(s)
    suppliers.append(s)

db.commit()
print(f"Loaded {len(alc_products)} beverage products from BegInv CSV")

# ── 3. SYNTHETIC RETAIL PRODUCTS (core supply chain items) ────────────────────
retail_data = [
    ("Rice (Basmati 5kg)",  "Grains",     "kg",      120, 5, 0.8,  60),
    ("Wheat Flour (10kg)",  "Grains",     "kg",      80,  4, 0.5,  45),
    ("Sugar (2kg)",         "Sweeteners", "kg",      100, 3, 0.6,  40),
    ("Cooking Oil (5L)",    "Oils",       "litre",   60,  4, 1.2,  55),
    ("Coffee Beans (1kg)",  "Beverages",  "kg",      40,  7, 2.5,  80),
    ("Black Tea (500g)",    "Beverages",  "pack",    50,  5, 1.0,  50),
    ("Lentils (1kg)",       "Pulses",     "kg",      90,  4, 0.7,  45),
    ("Olive Oil (1L)",      "Oils",       "litre",   35,  6, 2.0,  70),
    ("Pasta (500g)",        "Grains",     "pack",    85,  4, 0.5,  40),
    ("Tomato Paste (400g)", "Canned",     "can",     70,  3, 0.4,  35),
]
retail_suppliers = [
    ("AgriSupply Co", 0.92), ("FlourWorld", 0.95), ("SweetSource", 0.88),
    ("OilDepot", 0.90), ("BeanOrigin", 0.93), ("TeaHouse Exports", 0.87),
    ("PulseWorld", 0.91), ("MedOil Imports", 0.89), ("PastaItalia", 0.94),
    ("CanCo Supplies", 0.86),
]
base_prices = [12.0, 8.0, 5.5, 18.0, 45.0, 9.0, 6.5, 28.0, 4.0, 3.5]
stock_levels = [95, 200, 45, 150, 38, 120, 80, 30, 170, 200]

retail_products = []
for i, (name, cat, unit, rop, lt, hc, oc) in enumerate(retail_data):
    p = Product(name=name, category=cat, unit=unit, reorder_point=rop,
                lead_time_days=lt, holding_cost=hc, order_cost=oc)
    db.add(p)
    retail_products.append(p)

db.flush()

for i, p in enumerate(retail_products):
    db.add(Inventory(product_id=p.id, stock=stock_levels[i]))
    sname, rel = retail_suppliers[i]
    s = Supplier(name=sname, product_id=p.id, price_per_unit=base_prices[i],
                 lead_time_days=p.lead_time_days, reliability_score=rel)
    db.add(s)
    suppliers.append(s)

db.commit()
print(f"Loaded {len(retail_products)} retail products")

# ── 4. SALES HISTORY ──────────────────────────────────────────────────────────
# 4a. From SalesFINAL12312016.csv for alcohol products
sales_csv = pd.read_csv("data/SalesFINAL12312016.csv", parse_dates=["SalesDate"])
sales_csv = sales_csv.dropna(subset=["SalesDate", "SalesQuantity"])
beg_full = pd.read_csv("data/BegInvFINAL12312016.csv").drop_duplicates(subset=["Brand", "Description"]).head(30)
brand_to_pid = {int(row["Brand"]): p.id for (p, _, _), (_, row) in zip(alc_products, beg_full.iterrows())}

count = 0
for _, row in sales_csv.iterrows():
    try:
        pid = brand_to_pid.get(int(row["Brand"]))
    except:
        continue
    if pid:
        db.add(SalesHistory(product_id=pid, sale_date=row["SalesDate"].date(),
                            quantity_sold=float(row["SalesQuantity"])))
        count += 1
    if count % 5000 == 0 and count > 0:
        db.commit()
db.commit()
print(f"Loaded {count} alcohol sales records")

# 4b. From supply_chain_data.csv — use Number of products sold as monthly sales
sc_reload = pd.read_csv("data/supply_chain_data.csv").drop_duplicates(subset=["SKU"]).head(30)
sc_count = 0
start = date(2022, 1, 1)
for (p, _, _), (_, row) in zip(products, sc_reload.iterrows()):
    monthly_sold = float(row["Number of products sold"])
    daily_avg = monthly_sold / 30
    for i in range(365):
        d = start + timedelta(days=i)
        noise = np.random.normal(0, daily_avg * 0.1)
        qty = max(0.5, round(daily_avg + noise, 2))
        db.add(SalesHistory(product_id=p.id, sale_date=d, quantity_sold=qty))
        sc_count += 1
    if sc_count % 5000 == 0:
        db.commit()
db.commit()
print(f"Loaded {sc_count} supply chain product sales records")

# 4c. Synthetic 5-year sales for retail products
base_demands = [35, 28, 22, 18, 12, 15, 25, 8, 30, 20]
start5 = date(2019, 1, 1)
days5 = (date(2023, 12, 31) - start5).days + 1
retail_count = 0
for idx, p in enumerate(retail_products):
    base = base_demands[idx]
    for i in range(days5):
        d = start5 + timedelta(days=i)
        doy = d.timetuple().tm_yday
        yearly = math.sin(2 * math.pi * (doy - 80) / 365) * base * 0.35
        weekly = math.sin(2 * math.pi * d.weekday() / 7) * base * 0.15
        festive = base * 0.4 if d.month == 12 else (base * 0.2 if d.month in [4, 10] else 0)
        qty = max(1, round(base + yearly + weekly + festive + np.random.normal(0, base * 0.08), 2))
        db.add(SalesHistory(product_id=p.id, sale_date=d, quantity_sold=qty))
        retail_count += 1
    if retail_count % 10000 == 0:
        db.commit()
db.commit()
print(f"Loaded {retail_count} retail sales records (5 years)")

# ── 5. PURCHASE ORDERS ────────────────────────────────────────────────────────
# From PurchasesFINAL12312016.csv for alcohol
po_csv = pd.read_csv("data/PurchasesFINAL12312016.csv", parse_dates=["PODate"])
po_csv = po_csv.dropna(subset=["PODate", "Quantity"])
po_count = 0
for _, row in po_csv.iterrows():
    try:
        pid = brand_to_pid.get(int(row["Brand"]))
    except:
        continue
    if pid:
        db.add(PurchaseOrder(product_id=pid, supplier_id=None, quantity=float(row["Quantity"]),
                             status="Delivered", reason=f"PO#{row['PONumber']}"))
        po_count += 1
    if po_count % 2000 == 0 and po_count > 0:
        db.commit()
db.commit()
print(f"Loaded {po_count} alcohol purchase orders")

# Synthetic POs for retail + supply chain products
all_new = [(p, s) for (p, _, _), s in zip(products, suppliers[:30])] + \
          list(zip(retail_products, suppliers[-10:]))
syn_po = 0
for p, s in all_new:
    annual = base_demands[retail_products.index(p)] * 365 if p in retail_products else 500
    eoq = round(math.sqrt((2 * annual * p.order_cost) / max(p.holding_cost, 0.1)), 0)
    for i in range(0, days5, 45):
        d = start5 + timedelta(days=i)
        status = "Delivered" if d < date(2023, 10, 1) else ("In Transit" if d < date(2023, 12, 1) else "Draft")
        db.add(PurchaseOrder(product_id=p.id, supplier_id=s.id, quantity=eoq,
                             status=status, reason=f"Scheduled replenishment EOQ={eoq}"))
        syn_po += 1
db.commit()
print(f"Loaded {syn_po} synthetic purchase orders")

db.close()

total_products = len(products) + len(alc_products) + len(retail_products)
print(f"\nAll datasets loaded successfully!")
print(f"  Products   : {total_products} (30 supply chain + 30 beverages + 10 retail)")
print(f"  Suppliers  : {len(suppliers)}")
print(f"  Sales rows : {count + sc_count + retail_count}")
print(f"  POs        : {po_count + syn_po}")
