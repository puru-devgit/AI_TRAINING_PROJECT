import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_clients import get_inventory, get_orders

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #f78166, #d29922); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.savings-card { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 14px; padding: 22px; text-align: center; }
.savings-val { font-size: 1.9rem; font-weight: 700; }
.savings-lbl { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.impact-item { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 12px; padding: 16px 20px; margin: 8px 0; display: flex; align-items: center; gap: 14px; }
.impact-icon { font-size: 1.8rem; }
.impact-title { font-size: 0.95rem; font-weight: 600; color: #e6edf3; }
.impact-desc { font-size: 0.82rem; color: #8b949e; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">💰 Monthly Savings Report</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">Projected cost savings from AI-driven supply chain optimization</div>', unsafe_allow_html=True)

inventory = get_inventory()
orders = get_orders()

if not isinstance(inventory, list):
    st.error("Backend not reachable.")
    st.stop()

df = pd.DataFrame(inventory)

waste_saved = df[df["stock"] < df["reorder_point"]].shape[0] * 500
stockout_prevented = df[df["days_to_stockout"] < 7].shape[0]
lost_sales_prevented = stockout_prevented * 1200
holding_cost_saved = df[df["stock"] > df["reorder_point"] * 2].shape[0] * 300
total_savings = waste_saved + lost_sales_prevented + holding_cost_saved

# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="savings-card"><div class="savings-lbl">Waste Reduction</div><div class="savings-val" style="color:#3fb950">${waste_saved:,}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="savings-card"><div class="savings-lbl">Lost Sales Prevented</div><div class="savings-val" style="color:#58a6ff">${lost_sales_prevented:,}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="savings-card"><div class="savings-lbl">Holding Cost Saved</div><div class="savings-val" style="color:#a371f7">${holding_cost_saved:,}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="savings-card"><div class="savings-lbl">Total Monthly Savings</div><div class="savings-val" style="color:#d29922">${total_savings:,}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    categories = ["Waste Reduction", "Lost Sales Prevented", "Holding Cost Saved"]
    values = [waste_saved, lost_sales_prevented, holding_cost_saved]
    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=["#3fb950", "#58a6ff", "#a371f7"],
        text=[f"${v:,}" for v in values], textposition="outside",
    ))
    fig.update_layout(
        title="Monthly Savings Breakdown ($)",
        template="plotly_dark", height=380,
        paper_bgcolor="rgba(22,27,34,0.8)", plot_bgcolor="rgba(13,17,23,0.9)",
        font=dict(family="Inter", color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    status_counts = df.apply(
        lambda x: "Critical" if x["stock"] < x["reorder_point"]
        else ("Low" if x["stock"] < x["reorder_point"] * 1.5 else "Safe"), axis=1
    ).value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig2 = px.pie(status_counts, names="Status", values="Count",
                  color="Status",
                  color_discrete_map={"Critical": "#f85149", "Low": "#d29922", "Safe": "#3fb950"},
                  title="Current Inventory Health")
    fig2.update_layout(template="plotly_dark", height=380,
                       paper_bgcolor="rgba(22,27,34,0.8)",
                       font=dict(family="Inter", color="#c9d1d9"))
    st.plotly_chart(fig2, use_container_width=True)

# Business Impact
st.markdown('<div style="font-size:1.1rem;font-weight:600;color:#e6edf3;margin:20px 0 12px">📊 Business Impact Summary</div>', unsafe_allow_html=True)

impacts = [
    ("💸", "Revenue Protection", "Stockouts prevented on critical items, protecting customer revenue streams"),
    ("📦", "EOQ Optimization", "Order quantities mathematically optimized to minimize total inventory cost"),
    ("🤝", "Supplier Intelligence", "Best supplier selected per product based on price × reliability × lead time"),
    ("🤖", "24/7 Autonomous Monitoring", "AI agent continuously monitors stock and triggers reorders without manual effort"),
    ("📈", "Demand Forecasting", "Prophet model predicts seasonal demand spikes 30-90 days in advance"),
    ("⚠️", "Risk Intelligence", "RAG pipeline retrieves supply chain incident patterns to pre-empt disruptions"),
]
for icon, title, desc in impacts:
    st.markdown(f'<div class="impact-item"><div class="impact-icon">{icon}</div><div><div class="impact-title">{title}</div><div class="impact-desc">{desc}</div></div></div>', unsafe_allow_html=True)
