import pandas as pd

# =========================
# STEP 1: LOAD DATA
# =========================
sales = pd.read_csv("sales_weather_updated.csv")

# =========================
# STEP 2: REMOVE NULL VALUES
# =========================
sales.dropna(inplace=True)

# =========================
# STEP 3: REMOVE DUPLICATES
# =========================
sales.drop_duplicates(inplace=True)

# =========================
# STEP 4: FORMAT DATE COLUMN
# =========================
sales["date"] = pd.to_datetime(sales["date"], errors="coerce")

# Remove invalid dates
sales = sales.dropna(subset=["date"])

# =========================
# STEP 5: SORT DATA
# =========================
sales = sales.sort_values(by="date")

# =========================
# STEP 6: RESET INDEX
# =========================
sales.reset_index(drop=True, inplace=True)

# =========================
# STEP 7: SAVE CLEAN DATA
# =========================
sales.to_csv("sales_cleaned.csv", index=False)

print("✅ Dataset cleaned successfully!")