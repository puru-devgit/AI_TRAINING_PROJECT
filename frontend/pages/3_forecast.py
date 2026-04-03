import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.api_clients import get_forecast, get_sales_history, get_inventory

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #58a6ff, #3fb950); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-card { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 14px; padding: 20px; text-align: center; }
.stat-val { font-size: 1.8rem; font-weight: 700; color: #58a6ff; }
.stat-lbl { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">📈 AI Demand Forecast Engine</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">Powered by Facebook Prophet · Seasonal + Weekly + Festive patterns · 80% Confidence Intervals</div>', unsafe_allow_html=True)

inventory = get_inventory()
if not isinstance(inventory, list):
    st.error("Backend not reachable.")
    st.stop()

products = {p["product"]: p["id"] for p in inventory}

col1, col2 = st.columns([3, 1])
with col1:
    selected = st.selectbox("🛒 Select Product", list(products.keys()))
with col2:
    periods = st.slider("Forecast Days", 7, 90, 30)

product_id = products[selected]

with st.spinner("Running Prophet forecast model..."):
    result = get_forecast(product_id=product_id, periods=periods)

if "error" in result:
    st.error(f"Forecast error: {result['error']}")
    st.stop()

forecast = result.get("forecast", [])
if not forecast:
    st.warning("Not enough historical data to generate forecast.")
    st.stop()

fdf = pd.DataFrame(forecast)
fdf["date"] = pd.to_datetime(fdf["date"])

sales = get_sales_history(product_id=product_id)
sdf = pd.DataFrame(sales) if isinstance(sales, list) and sales else pd.DataFrame()
if not sdf.empty:
    sdf["date"] = pd.to_datetime(sdf["date"])
    sdf = sdf.tail(365)

# Chart
fig = go.Figure()

if not sdf.empty:
    fig.add_trace(go.Scatter(
        x=sdf["date"], y=sdf["quantity_sold"],
        mode="lines", name="Historical Sales",
        line=dict(color="#58a6ff", width=1), opacity=0.5,
        fill="tozeroy", fillcolor="rgba(88,166,255,0.05)",
    ))

fig.add_trace(go.Scatter(
    x=pd.concat([fdf["date"], fdf["date"][::-1]]),
    y=pd.concat([fdf["upper"], fdf["lower"][::-1]]),
    fill="toself", fillcolor="rgba(163,113,247,0.12)",
    line=dict(color="rgba(255,255,255,0)"),
    name="80% Confidence Interval",
    hoverinfo="skip",
))

fig.add_trace(go.Scatter(
    x=fdf["date"], y=fdf["predicted_demand"],
    mode="lines+markers", name="AI Forecast",
    line=dict(color="#a371f7", width=2.5),
    marker=dict(size=5, color="#a371f7"),
))

fig.update_layout(
    title=dict(text=f"Demand Forecast — {selected} ({periods} days)", font=dict(size=16, color="#e6edf3")),
    xaxis_title="Date", yaxis_title="Units / Day",
    template="plotly_dark", height=500,
    paper_bgcolor="rgba(22,27,34,0.9)", plot_bgcolor="rgba(13,17,23,0.9)",
    font=dict(family="Inter", color="#c9d1d9"),
    xaxis=dict(gridcolor="#21262d", showgrid=True),
    yaxis=dict(gridcolor="#21262d", showgrid=True),
    legend=dict(orientation="h", y=-0.15, bgcolor="rgba(0,0,0,0)"),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# Stats
avg = fdf["predicted_demand"].mean()
peak = fdf["predicted_demand"].max()
low_val = fdf["predicted_demand"].min()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-lbl">Avg Forecast</div><div class="stat-val">{avg:.1f}</div><div style="color:#8b949e;font-size:0.8rem">units/day</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-lbl">Peak Demand</div><div class="stat-val" style="color:#f85149">{peak:.1f}</div><div style="color:#8b949e;font-size:0.8rem">units/day</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-lbl">Min Demand</div><div class="stat-val" style="color:#3fb950">{low_val:.1f}</div><div style="color:#8b949e;font-size:0.8rem">units/day</div></div>', unsafe_allow_html=True)
with c4:
    total = avg * periods
    st.markdown(f'<div class="stat-card"><div class="stat-lbl">Total Projected</div><div class="stat-val" style="color:#d29922">{total:.0f}</div><div style="color:#8b949e;font-size:0.8rem">units in {periods}d</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
if avg > 25:
    st.warning("📈 High demand expected — consider increasing stock levels and placing early POs!")
else:
    st.success("📉 Demand is stable within normal range.")

st.markdown('<div style="font-size:1.1rem;font-weight:600;color:#e6edf3;margin:20px 0 10px">📋 Forecast Table</div>', unsafe_allow_html=True)
st.dataframe(
    fdf.rename(columns={"date": "Date", "predicted_demand": "Forecast (units)", "upper": "Upper CI", "lower": "Lower CI"}),
    use_container_width=True, height=300,
)
