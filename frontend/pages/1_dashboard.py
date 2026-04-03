import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_clients import get_inventory, get_sales_history
from utils.helpers import calculate_status, detect_risk, format_number

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.section-title { font-size: 1.1rem; font-weight: 600; color: #e6edf3; margin: 20px 0 10px 0; }
.kpi-card { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 14px; padding: 20px; text-align: center; }
.kpi-val { font-size: 2rem; font-weight: 700; color: #58a6ff; }
.kpi-lbl { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📊 Smart Inventory Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">Real-time stock intelligence with AI risk detection</div>', unsafe_allow_html=True)

inventory = get_inventory()
if not isinstance(inventory, list) or not inventory:
    st.error("Backend not reachable.")
    st.stop()

df = pd.DataFrame(inventory)
df["status"] = df.apply(lambda x: calculate_status(x["stock"], x["reorder_point"]), axis=1)
df["risk"] = df.apply(lambda x: detect_risk(x["stock"], x["reorder_point"]), axis=1)

# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Products</div><div class="kpi-val">{len(df)}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Total Stock</div><div class="kpi-val">{format_number(df["stock"].sum())}</div></div>', unsafe_allow_html=True)
with c3:
    n = df[df["status"].str.contains("Critical")].shape[0]
    st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Critical</div><div class="kpi-val" style="color:#f85149">{n}</div></div>', unsafe_allow_html=True)
with c4:
    n = df[df["status"].str.contains("Low")].shape[0]
    st.markdown(f'<div class="kpi-card"><div class="kpi-lbl">Low Stock</div><div class="kpi-val" style="color:#d29922">{n}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Stock Levels Chart
color_map = {"🔴 Critical": "#f85149", "🟡 Low": "#d29922", "🟢 Safe": "#3fb950"}
fig = px.bar(df, x="product", y="stock", color="status",
             color_discrete_map=color_map, text="stock",
             title="Stock Levels vs Reorder Points")
fig.add_scatter(x=df["product"], y=df["reorder_point"], mode="markers+lines",
                name="Reorder Point", line=dict(color="#58a6ff", dash="dash", width=2),
                marker=dict(size=8, color="#58a6ff"))
fig.update_layout(
    template="plotly_dark", height=420,
    paper_bgcolor="rgba(22,27,34,0.8)", plot_bgcolor="rgba(22,27,34,0.8)",
    font=dict(family="Inter", color="#c9d1d9"),
    title_font=dict(size=16, color="#e6edf3"),
    xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
    legend=dict(orientation="h", y=-0.2),
)
fig.update_traces(selector=dict(type='bar'), texttemplate="%{text:.0f}", textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# Days to Stockout
fig2 = px.bar(df, x="product", y="days_to_stockout", color="status",
              color_discrete_map=color_map, text="days_to_stockout",
              title="Estimated Days Until Stockout")
fig2.update_layout(
    template="plotly_dark", height=380,
    paper_bgcolor="rgba(22,27,34,0.8)", plot_bgcolor="rgba(22,27,34,0.8)",
    font=dict(family="Inter", color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
    legend=dict(orientation="h", y=-0.2),
)
fig2.update_traces(selector=dict(type='bar'), texttemplate="%{text:.0f}d", textposition="outside")
st.plotly_chart(fig2, use_container_width=True)

# Sales Trend
st.markdown('<div class="section-title">📈 Sales History</div>', unsafe_allow_html=True)
products_map = {p["product"]: p["id"] for p in inventory}
selected = st.selectbox("Select product", list(products_map.keys()))
sales = get_sales_history(product_id=products_map[selected])
if isinstance(sales, list) and sales:
    sdf = pd.DataFrame(sales)
    sdf["date"] = pd.to_datetime(sdf["date"])
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=sdf["date"], y=sdf["quantity_sold"],
                              mode="lines", name="Daily Sales",
                              line=dict(color="#58a6ff", width=1.5),
                              fill="tozeroy", fillcolor="rgba(88,166,255,0.08)"))
    fig3.update_layout(
        title=f"Daily Sales — {selected}",
        template="plotly_dark", height=380,
        paper_bgcolor="rgba(22,27,34,0.8)", plot_bgcolor="rgba(22,27,34,0.8)",
        font=dict(family="Inter", color="#c9d1d9"),
        xaxis=dict(gridcolor="#21262d"), yaxis=dict(gridcolor="#21262d"),
    )
    st.plotly_chart(fig3, use_container_width=True)
