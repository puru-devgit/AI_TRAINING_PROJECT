# ================================
# DAY 1: BASIC TEST (DUMMY DATA)
# ================================

from prophet import Prophet
import pandas as pd

print("\n===== DAY 1: BASIC FORECAST =====")

# Sample data
data = {
    "ds": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
    "y": [100, 120, 130, 90]
}

df_day1 = pd.DataFrame(data)
df_day1["ds"] = pd.to_datetime(df_day1["ds"])

# Model
model1 = Prophet()
model1.fit(df_day1)

future1 = model1.make_future_dataframe(periods=5)
forecast1 = model1.predict(future1)

print(forecast1[["ds", "yhat"]].tail())


# ================================
# DAY 2: REAL DATA FORECAST
# ================================

print("\n===== DAY 2: REAL DATA FORECAST =====")

# Load dataset
df = pd.read_csv("sales_weather_updated.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Select needed columns
df = df[["date", "units_sold"]]

# Rename for Prophet
df.rename(columns={
    "date": "ds",
    "units_sold": "y"
}, inplace=True)

# Convert date
df["ds"] = pd.to_datetime(df["ds"])

# Model
model2 = Prophet()
model2.fit(df)

# Predict
future2 = model2.make_future_dataframe(periods=15)
forecast2 = model2.predict(future2)

print(forecast2[["ds", "yhat"]].tail())


# ================================
# DAY 3: DECISION MAKING
# ================================

print("\n===== DAY 3: DECISION MAKING =====")

# Predict longer period
future3 = model2.make_future_dataframe(periods=30)
forecast3 = model2.predict(future3)

# Extract future demand
future_demand = forecast3["yhat"].iloc[-1]
print("Predicted Future Demand:", future_demand)

# Decision logic
current_stock = 200

if future_demand > current_stock:
    print("Reorder needed")
else:
    print("Stock is enough")


# ================================
# SAVE OUTPUT (OPTIONAL)
# ================================

forecast3.to_csv("forecast_output.csv", index=False)

print("\nForecast saved as forecast_output.csv")