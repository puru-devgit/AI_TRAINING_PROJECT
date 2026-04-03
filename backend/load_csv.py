import pandas as pd
from database import engine, SessionLocal
from models import Base, Product, Inventory, SalesHistory, Supplier, PurchaseOrder
from sqlalchemy import text

db = SessionLocal()

# Clear existing data
db.execute(text("TRUNCATE products, inventory, sales_history, suppliers, purchase_orders RESTART IDENTITY CASCADE"))
db.commit()
print("Cleared existing data")

# --- 1. Products + Inventory from BegInv ---
beg = pd.read_csv("data/BegInvFINAL12312016.csv")
beg = beg.drop_duplicates(subset=["Brand", "Description"]).head(50)

products = []
for _, row in beg.iterrows():
    p = Product(
        name=str(row["Description"])[:100],
        category=str(row.get("Classification", "General")),
        unit="units",
        reorder_point=round(float(row["onHand"]) * 0.3, 2),
        lead_time_days=5,
        holding_cost=round(float(row["Price"]) * 0.02, 2),
        order_cost=50.0,
    )
    db.add(p)
    products.append((p, float(row["onHand"])))

db.flush()

for p, stock in products:
    db.add(Inventory(product_id=p.id, stock=stock))

db.commit()
print(f"Loaded {len(products)} products + inventory")

# --- 2. Suppliers from PurchasePrices ---
prices = pd.read_csv("data/2017PurchasePricesDec.csv")
prices = prices.drop_duplicates(subset=["VendorNumber", "Description"])

product_map = {p.name: p.id for p, _ in products}
count = 0
for _, row in prices.iterrows():
    name = str(row["Description"])[:100]
    if name in product_map:
        db.add(Supplier(
            name=str(row["VendorName"])[:100],
            product_id=product_map[name],
            price_per_unit=float(row["PurchasePrice"]),
            lead_time_days=5,
            reliability_score=0.85,
        ))
        count += 1

db.commit()
print(f"Loaded {count} suppliers")

# Brand -> product_id map (Brand column in CSVs matches Brand in BegInv)
beg_full = pd.read_csv("data/BegInvFINAL12312016.csv").drop_duplicates(subset=["Brand", "Description"]).head(50)
brand_to_pid = {}
for (p, _), (_, row) in zip(products, beg_full.iterrows()):
    brand_to_pid[int(row["Brand"])] = p.id

# --- 3. Sales History ---
sales = pd.read_csv("data/SalesFINAL12312016.csv", parse_dates=["SalesDate"])
sales = sales.dropna(subset=["SalesDate", "SalesQuantity"])

count = 0
for _, row in sales.iterrows():
    pid = brand_to_pid.get(int(row["Brand"]))
    if pid:
        db.add(SalesHistory(
            product_id=pid,
            sale_date=row["SalesDate"].date(),
            quantity_sold=float(row["SalesQuantity"]),
        ))
        count += 1
    if count % 5000 == 0 and count > 0:
        db.commit()

db.commit()
print(f"Loaded {count} sales records")

# --- 4. Purchase Orders ---
po = pd.read_csv("data/PurchasesFINAL12312016.csv", parse_dates=["PODate"])
po = po.dropna(subset=["PODate", "Quantity"])

count = 0
for _, row in po.iterrows():
    pid = brand_to_pid.get(int(row["Brand"]))
    if pid:
        db.add(PurchaseOrder(
            product_id=pid,
            supplier_id=None,
            quantity=float(row["Quantity"]),
            status="Delivered",
            reason=f"PO#{row['PONumber']}",
        ))
        count += 1
    if count % 2000 == 0 and count > 0:
        db.commit()

db.commit()
print(f"Loaded {count} purchase orders")

db.close()
print("All CSV data loaded successfully!")
