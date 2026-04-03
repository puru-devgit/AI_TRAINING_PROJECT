import streamlit as st
import pandas as pd
import requests
from utils.api_clients import get_inventory
from utils.helpers import calculate_status

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.product-card { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 14px; padding: 20px; margin: 8px 0; transition: all 0.2s; }
.product-card:hover { border-color: #58a6ff; }
.badge { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge-critical { background: rgba(248,81,73,0.15); color: #f85149; border: 1px solid #f85149; }
.badge-low { background: rgba(210,153,34,0.15); color: #d29922; border: 1px solid #d29922; }
.badge-safe { background: rgba(63,185,80,0.15); color: #3fb950; border: 1px solid #3fb950; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📦 Inventory Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">Live stock monitoring with ROP tracking and inline updates</div>', unsafe_allow_html=True)

data = get_inventory()
if not isinstance(data, list) or not data:
    st.error("Backend not reachable.")
    st.stop()

df = pd.DataFrame(data)
df["status"] = df.apply(lambda x: calculate_status(x["stock"], x["reorder_point"]), axis=1)

col1, col2 = st.columns([2, 1])
with col1:
    product_filter = st.selectbox("🔍 Filter by Product", ["All"] + list(df["product"]))
with col2:
    status_filter = st.selectbox("📊 Filter by Status", ["All", "🔴 Critical", "🟡 Low", "🟢 Safe"])

view = df.copy()
if product_filter != "All":
    view = view[view["product"] == product_filter]
if status_filter != "All":
    view = view[view["status"] == status_filter]

# Table
st.markdown("<br>", unsafe_allow_html=True)
st.dataframe(
    view[["product", "category", "stock", "unit", "reorder_point", "lead_time", "avg_daily_demand", "days_to_stockout", "status"]].rename(columns={
        "product": "Product", "category": "Category", "stock": "Stock",
        "unit": "Unit", "reorder_point": "ROP", "lead_time": "Lead Time (days)",
        "avg_daily_demand": "Avg Daily Demand", "days_to_stockout": "Days to Stockout", "status": "Status"
    }),
    use_container_width=True, height=300,
)

# Product Cards
st.markdown('<div style="font-size:1.1rem;font-weight:600;color:#e6edf3;margin:24px 0 12px">📊 Product Details</div>', unsafe_allow_html=True)
for _, row in view.iterrows():
    badge_class = "badge-critical" if "Critical" in row["status"] else ("badge-low" if "Low" in row["status"] else "badge-safe")
    badge_text = "CRITICAL" if "Critical" in row["status"] else ("LOW STOCK" if "Low" in row["status"] else "SAFE")
    with st.expander(f"{row['product']}  —  {row['status']}"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Stock", f"{row['stock']} {row['unit']}")
        c2.metric("Reorder Point", f"{row['reorder_point']}")
        c3.metric("Days to Stockout", f"{row['days_to_stockout']}")
        c4.metric("Avg Daily Demand", f"{row['avg_daily_demand']}")

        pct = min(int((row["stock"] / max(row["reorder_point"] * 2, 1)) * 100), 100)
        st.progress(pct / 100, text=f"Stock level: {pct}%")

        new_stock = st.number_input(f"Update stock", min_value=0.0,
                                    value=float(row["stock"]), step=1.0, key=f"stock_{row['id']}")
        if st.button(f"💾 Update Stock", key=f"btn_{row['id']}", type="primary"):
            try:
                r = requests.put(f"http://localhost:8000/inventory/{row['id']}/stock",
                                 params={"stock": new_stock}, timeout=5)
                st.success(f"Stock updated to {new_stock} {row['unit']}")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {e}")
