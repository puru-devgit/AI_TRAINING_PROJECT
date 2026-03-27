import streamlit as st
import pandas as pd
from utils.api_clients import get_inventory

st.header("📦 Inventory Management")

data = get_inventory()
df = pd.DataFrame(data)

if df.empty:
    st.warning("No inventory data available")
else:
    def get_status(row):
        if row["stock"] < row["reorder_point"]:
            return "🔴 Critical"
        elif row["stock"] < row["reorder_point"] * 1.5:
            return "🟡 Low"
        else:
            return "🟢 Safe"

    df["status"] = df.apply(get_status, axis=1)

    st.dataframe(df)

    st.subheader("🔍 Filter")
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Safe", "Low", "Critical"]
    )

    if status_filter != "All":
        st.dataframe(df[df["status"].str.contains(status_filter)])