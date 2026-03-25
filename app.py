import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Supply Chain", layout="wide")

# SIDEBAR
st.sidebar.title("📂 Menu")
option = st.sidebar.selectbox(
    "Choose Section",
    ["Home", "Inventory"]
)

# DUMMY DATA
data = [
    {"Product": "Rice", "Stock": 50},
    {"Product": "Wheat", "Stock": 20},
    {"Product": "Sugar", "Stock": 10},
    {"Product": "Oil", "Stock": 5}
]

df = pd.DataFrame(data)

# ---------------- HOME PAGE ----------------
if option == "Home":
    st.title("📦 AI Supply Chain Dashboard")

    st.markdown("### 📊 Overview")

    col1, col2, col3 = st.columns(3)

    total_products = len(data)
    low_stock = len([d for d in data if d["Stock"] < 15])
    total_stock = sum([d["Stock"] for d in data])

    col1.metric("Total Products", total_products)
    col2.metric("Low Stock Items ⚠️", low_stock)
    col3.metric("Total Stock", total_stock)

    st.markdown("---")

    st.subheader("📢 System Status")
    st.success("✅ System is running smoothly!")

# ---------------- INVENTORY PAGE ----------------
elif option == "Inventory":
    st.title("📦 Inventory Management")

    st.markdown("### 📋 Stock Details")

    # Styled table
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    st.subheader("⚠️ Alerts")

    for item in data:
        if item["Stock"] < 15:
            st.error(f"Low stock: {item['Product']} (Only {item['Stock']} left!)")

    st.markdown("---")

    st.subheader("📊 Stock Level Visualization")

    for item in data:
        st.write(f"{item['Product']}")
        st.progress(item["Stock"] / 100)