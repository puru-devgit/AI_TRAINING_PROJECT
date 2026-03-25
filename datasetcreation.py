import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
# 1. INVENTORY DATA (1000 rows)
n_products = 1000

inventory = pd.DataFrame({
    "product_id": np.arange(1001, 1001 + n_products),
    "product_name": [f"Product_{i}" for i in range(1, n_products + 1)],
    "category": np.random.choice(["Food", "Dairy", "Hygiene", "Snacks", "Beverages"], n_products),
    "stock_quantity": np.random.randint(50, 1000, n_products),
    "holding_cost": np.round(np.random.uniform(0.5, 5.0, n_products), 2),
    "lead_time_days": np.random.randint(1, 10, n_products)
})

# Calculate ROP and EOQ
avg_daily_sales = np.random.randint(5, 60, n_products)
ordering_cost = 50

inventory["reorder_point"] = avg_daily_sales * inventory["lead_time_days"]
inventory["economic_order_quantity"] = np.sqrt(
    (2 * avg_daily_sales * 365 * ordering_cost) / inventory["holding_cost"]
).astype(int)

inventory.to_csv("inventory_1000.csv", index=False)

# 2. SALES DATA (1000+ rows)
sales_data = []

start_date = datetime(2025, 1, 1)

for i in range(1000):
    product_id = np.random.choice(inventory["product_id"])
    
    # Create realistic date pattern
    date = start_date + timedelta(days=i % 180)
    
    # Demand with variation
    units_sold = max(1, int(np.random.normal(30, 10)))
    
    sales_data.append([date.strftime("%Y-%m-%d"), product_id, units_sold])

sales = pd.DataFrame(sales_data, columns=["date", "product_id", "units_sold"])
sales.to_csv("sales_1000.csv", index=False)
# 3. SUPPLIERS DATA (1000 rows)
suppliers = pd.DataFrame({
    "supplier_id": np.arange(1, 1001),
    "supplier_name": [f"Supplier_{i}" for i in range(1, 1001)],
    "product_id": np.random.choice(inventory["product_id"], 1000),
    "delivery_time_days": np.random.randint(1, 10, 1000),
    "cost_per_unit": np.round(np.random.uniform(10, 100, 1000), 2),
    "risk_level": np.random.choice(["Low", "Medium", "High"], 1000)
})

suppliers.to_csv("suppliers_1000.csv", index=False)


print("All datasets created successfully!")