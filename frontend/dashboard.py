import streamlit as st
import pandas as pd
from utils.api_clients import get_inventory, get_sales

st.header("📊 Dashboard")

with st.spinner("Loading data..."):
    inventory = get_inventory()
    sales = get_sales()

df = pd.DataFrame(inventory)

col1, col2, col3 = st.columns(3)

if not df.empty:
    total_stock = df["stock"].sum()
    low_stock = df[df["stock"] < df["reorder_point"]].shape[0]

    col1.metric("Total Products", len(df))
    col2.metric("Total Stock", total_stock)
    col3.metric("Low Stock Items", low_stock)

    st.subheader("📦 Inventory Table")
    st.dataframe(df)

    # Alerts
    low_df = df[df["stock"] < df["reorder_point"]]
    if not low_df.empty:
        st.error("⚠️ Low Stock Alert!")
        st.dataframe(low_df)
    else:
        st.success("✅ All inventory levels are safe")

# Sales chart
sales_df = pd.DataFrame(sales)
if not sales_df.empty:
    st.subheader("📈 Sales Trend")
    st.line_chart(sales_df.set_index("date")["quantity_sold"])