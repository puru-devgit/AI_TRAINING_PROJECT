import streamlit as st
import pandas as pd
from utils.api_clients import get_inventory, get_weather
from utils.helpers import calculate_status, format_number

st.set_page_config(page_title="SupplyMind AI", layout="wide", page_icon="🧠")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 50%, #0a0e1a 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }

.metric-card {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.metric-card:hover { border-color: #58a6ff; transform: translateY(-2px); box-shadow: 0 8px 30px rgba(88,166,255,0.15); }
.metric-value { font-size: 2.4rem; font-weight: 700; color: #58a6ff; margin: 8px 0; }
.metric-label { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
.metric-delta { font-size: 0.8rem; margin-top: 4px; }

.hero-title {
    font-size: 2.8rem; font-weight: 700;
    background: linear-gradient(135deg, #58a6ff, #a371f7, #f78166);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.hero-sub { color: #8b949e; font-size: 1rem; margin-bottom: 24px; }

.weather-card {
    background: linear-gradient(135deg, #1c2128, #21262d);
    border: 1px solid #30363d; border-left: 4px solid #58a6ff;
    border-radius: 12px; padding: 16px 20px;
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 24px;
}
.alert-critical {
    background: linear-gradient(135deg, #2d1117, #3d1a1a);
    border: 1px solid #f85149; border-left: 4px solid #f85149;
    border-radius: 12px; padding: 14px 18px; margin: 6px 0;
    color: #ffa198;
}
.alert-low {
    background: linear-gradient(135deg, #2d2000, #3d2e00);
    border: 1px solid #d29922; border-left: 4px solid #d29922;
    border-radius: 12px; padding: 14px 18px; margin: 6px 0;
    color: #e3b341;
}
.alert-safe {
    background: linear-gradient(135deg, #0d2d1a, #122d1a);
    border: 1px solid #3fb950; border-left: 4px solid #3fb950;
    border-radius: 12px; padding: 14px 18px; margin: 6px 0;
    color: #56d364;
}
.section-title {
    font-size: 1.2rem; font-weight: 600; color: #e6edf3;
    margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px;
}
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600;
}
.badge-critical { background: rgba(248,81,73,0.2); color: #f85149; border: 1px solid #f85149; }
.badge-low { background: rgba(210,153,34,0.2); color: #d29922; border: 1px solid #d29922; }
.badge-safe { background: rgba(63,185,80,0.2); color: #3fb950; border: 1px solid #3fb950; }

[data-testid="stMetricValue"] { color: #58a6ff !important; font-size: 2rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }
</style>
""", unsafe_allow_html=True)

# Hero
st.markdown('<div class="hero-title">🧠 SupplyMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Autonomous Supply Chain Optimization · Prophet Forecasting · LangChain ReAct Agent · PostgreSQL</div>', unsafe_allow_html=True)

# Weather Signal
weather = get_weather("Mumbai")
if "error" not in weather:
    signal_color = "#f85149" if weather.get("demand_signal") == "high" else "#3fb950"
    st.markdown(f"""
    <div class="weather-card">
        <span style="font-size:2rem">🌤️</span>
        <div>
            <div style="color:#e6edf3;font-weight:600">{weather['city']} Weather Signal</div>
            <div style="color:#8b949e;font-size:0.9rem">{weather['temperature']}°C · {weather['description']} · Humidity {weather['humidity']}%</div>
        </div>
        <div style="margin-left:auto;text-align:right">
            <div style="color:#8b949e;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px">Demand Signal</div>
            <div style="color:{signal_color};font-weight:700;font-size:1.1rem">{weather.get('demand_signal','N/A').upper()}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# KPIs
inventory = get_inventory()
if isinstance(inventory, list) and inventory:
    df = pd.DataFrame(inventory)
    df["status"] = df.apply(lambda x: calculate_status(x["stock"], x["reorder_point"]), axis=1)
    total_stock = df["stock"].sum()
    critical = df[df["status"].str.contains("Critical")].shape[0]
    low = df[df["status"].str.contains("Low")].shape[0]
    avg_days = df["days_to_stockout"].replace(float("inf"), 999).mean()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Products</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Stock Units</div><div class="metric-value">{format_number(total_stock)}</div></div>', unsafe_allow_html=True)
    with c3:
        color = "#f85149" if critical > 0 else "#3fb950"
        st.markdown(f'<div class="metric-card"><div class="metric-label">Critical Items</div><div class="metric-value" style="color:{color}">{critical}</div><div class="metric-delta" style="color:#8b949e">Need immediate reorder</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Days to Stockout</div><div class="metric-value">{avg_days:.1f}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🚨 Live Risk Alerts</div>', unsafe_allow_html=True)
    for _, row in df.iterrows():
        days = row["days_to_stockout"]
        days_str = f"{days}" if days != 999 else "∞"
        if "Critical" in row["status"]:
            st.markdown(f'<div class="alert-critical"><strong>{row["product"]}</strong> &nbsp;<span class="badge badge-critical">CRITICAL</span>&nbsp; Stock: <strong>{row["stock"]} {row["unit"]}</strong> · ROP: {row["reorder_point"]} · Days left: <strong>{days_str}</strong> ⚠️ REORDER NOW</div>', unsafe_allow_html=True)
        elif "Low" in row["status"]:
            st.markdown(f'<div class="alert-low"><strong>{row["product"]}</strong> &nbsp;<span class="badge badge-low">LOW</span>&nbsp; Stock: <strong>{row["stock"]} {row["unit"]}</strong> · ROP: {row["reorder_point"]} · Days left: {days_str}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-safe"><strong>{row["product"]}</strong> &nbsp;<span class="badge badge-safe">SAFE</span>&nbsp; Stock: <strong>{row["stock"]} {row["unit"]}</strong> ✓</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert-critical">⚠️ Cannot connect to backend. Make sure FastAPI is running on port 8000.</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div style="text-align:center;padding:16px 0 8px">
    <div style="font-size:2rem">🧠</div>
    <div style="font-size:1.1rem;font-weight:700;color:#e6edf3">SupplyMind AI</div>
    <div style="font-size:0.75rem;color:#8b949e;margin-top:4px">Supply Chain Intelligence</div>
</div>
<hr style="border-color:#21262d;margin:12px 0">
""", unsafe_allow_html=True)
st.sidebar.markdown("**Navigation**")
