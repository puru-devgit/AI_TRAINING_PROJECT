"""
utils/helpers.py
────────────────
Shared utilities for the SupplyMind frontend.
Imported by every page module.

Contents
  - DESIGN_CSS      : global dark-industrial stylesheet
  - PRODUCTS        : seed inventory data (mock fallback)
  - api_*()         : cached API helpers with mock fallbacks
  - _make_history() : synthetic 120-day sales data
  - PLOTLY_THEME    : shared Plotly layout dict
"""

import math
import random
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

# ── backend URL ───────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

# ══════════════════════════════════════════════════════════════════
# GLOBAL CSS
# Aesthetic: deep-space dark · electric-cyan accent
# Display font: Rajdhani  ·  Data font: JetBrains Mono
# ══════════════════════════════════════════════════════════════════
DESIGN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"]   { font-family: 'Rajdhani', sans-serif; }
.stApp                        { background: #06080f; color: #c6cce0; }

/* sidebar */
section[data-testid="stSidebar"] {
    background: #080b16 !important;
    border-right: 1px solid #101828;
}
section[data-testid="stSidebar"] .stRadio label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    color: #3a4560 !important;
    letter-spacing: .04em;
    transition: color .15s;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #00e5cc !important; }

/* headings */
h1 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important; font-size: 2rem !important;
    color: #e8edf8 !important; letter-spacing: .04em;
    line-height: 1.1 !important; margin-bottom: 0 !important;
}
h2 {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important; font-size: .72rem !important;
    color: #1e2d45 !important; text-transform: uppercase;
    letter-spacing: .2em; margin-top: 2rem !important;
}

/* metric cards */
div[data-testid="metric-container"] {
    background: #080c1a; border: 1px solid #101828;
    border-left: 3px solid #00e5cc;
    border-radius: 3px 8px 8px 3px;
    padding: 1rem 1.2rem .9rem;
}
div[data-testid="metric-container"] label {
    color: #1e2d45 !important; font-size: 9px !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase; letter-spacing: .18em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 2.1rem !important; font-weight: 700 !important;
    color: #e8edf8 !important; line-height: 1.1 !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important;
}

/* dividers */
hr { border-color: #101828 !important; margin: 1.3rem 0 !important; }

/* dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 8px; overflow: hidden; border: 1px solid #101828;
}

/* selectbox */
div[data-testid="stSelectbox"] > div {
    background: #080c1a !important; border: 1px solid #101828 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
}

/* text input */
div[data-testid="stTextInput"] input {
    background: #080c1a !important; border: 1px solid #101828 !important;
    border-radius: 6px !important; color: #c6cce0 !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
}

/* buttons */
.stButton > button {
    background: transparent; color: #00e5cc; border: 1px solid #00e5cc;
    border-radius: 4px; font-family: 'JetBrains Mono', monospace;
    font-size: 11px; letter-spacing: .06em; padding: .3rem .9rem;
    transition: all .15s;
}
.stButton > button:hover { background: #00e5cc; color: #06080f; }

/* expander */
details summary {
    font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important;
}

/* ── reusable components ──────────────────────────────── */

/* page header */
.ph {
    border-left: 3px solid #00e5cc;
    padding: .45rem 0 .45rem 1rem; margin-bottom: 1.4rem;
}
.ph p {
    margin: 0; color: #1e2d45;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: .03em;
}

/* section micro-label */
.slbl {
    font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #1e2d45;
    text-transform: uppercase; letter-spacing: .18em; margin: 1.6rem 0 .5rem;
}

/* 3-col stat grid */
.kgrid {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 1px; background: #101828; border-radius: 8px;
    overflow: hidden; margin-bottom: 1.2rem;
}
.kcell  { background: #080c1a; padding: .85rem 1rem; }
.kcell .kl {
    font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #1e2d45;
    text-transform: uppercase; letter-spacing: .16em;
}
.kcell .kv {
    font-family: 'Rajdhani', sans-serif; font-size: 1.5rem;
    font-weight: 700; color: #e8edf8; margin-top: 1px;
}
.kv.tc  { color: #00e5cc; }
.kv.red { color: #ff6b6b; }
.kv.grn { color: #51cf66; }

/* alert row */
.arow {
    display: flex; align-items: center; gap: 10px;
    padding: .6rem .95rem; border-radius: 6px; margin-bottom: 5px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
}
.arow.cr { background:#160808; border:1px solid #2e1010; color:#ff9999; }
.arow.wn { background:#160e00; border:1px solid #2e2000; color:#ffd580; }
.abg { padding:1px 7px; border-radius:3px; font-size:9px; letter-spacing:.06em; flex-shrink:0; }
.abg.cr { background:#4a1010; color:#ff9999; }
.abg.wn { background:#4a2e00; color:#ffd580; }

/* weather strip */
.ws {
    background:#060e1c; border:1px solid #0d2035; border-left:3px solid #3b9eff;
    border-radius:0 6px 6px 0; padding:.6rem 1rem;
    font-family:'JetBrains Mono',monospace; font-size:11px; color:#5aabff;
    margin-bottom:1.2rem; letter-spacing:.03em;
}

/* connection badge */
.cb {
    display:inline-flex; align-items:center; gap:5px;
    padding:2px 9px; border-radius:3px;
    font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:.08em;
}
.cb.on  { background:#031a0e; color:#00e5cc; border:1px solid #0a4a2a; }
.cb.off { background:#160808; color:#ff6b6b; border:1px solid #4a1010; }
.cd { width:5px; height:5px; border-radius:50%; background:currentColor; }

/* holdout accuracy card */
.hc { background:#080c1a; border:1px solid #101828; border-radius:8px; padding:1.1rem 1.3rem; }
.hc .ht {
    font-family:'Rajdhani',sans-serif; font-weight:600; font-size:.85rem;
    color:#3a4560; text-transform:uppercase; letter-spacing:.14em; margin-bottom:.8rem;
}
.mrow { display:flex; gap:20px; flex-wrap:wrap; margin-bottom:.6rem; }
.mi .ml { font-family:'JetBrains Mono',monospace; font-size:9px; color:#1e2d45; text-transform:uppercase; letter-spacing:.14em; }
.mi .mv { font-family:'Rajdhani',sans-serif; font-size:1.45rem; font-weight:700; color:#00e5cc; }
.hfoot  { font-family:'JetBrains Mono',monospace; font-size:10px; color:#1e2d45; line-height:1.7; margin-top:.6rem; }

/* agent chat bubble */
.chat-wrap { display:flex; flex-direction:column; gap:10px; }
.bubble {
    max-width:82%; padding:.75rem 1rem; border-radius:8px; line-height:1.6;
    font-family:'JetBrains Mono',monospace; font-size:12px;
}
.bubble.user {
    align-self:flex-end; background:#0d1a2e; border:1px solid #1a3050; color:#7dd3fc;
}
.bubble.agent {
    align-self:flex-start; background:#080c18; border:1px solid #101828; color:#c6cce0;
}
.bubble.agent b { color:#00e5cc; }
.bubble.system {
    align-self:center; background:transparent; border:1px dashed #1e2d45;
    color:#1e2d45; font-size:10px; padding:.35rem .8rem; border-radius:4px;
}

/* PO card */
.po-card {
    background:#080c1a; border:1px solid #101828; border-left:3px solid #00e5cc;
    border-radius:0 8px 8px 0; padding:1rem 1.2rem; margin-bottom:.8rem;
}
.po-card .po-title {
    font-family:'Rajdhani',sans-serif; font-weight:700; font-size:1rem;
    color:#e8edf8; letter-spacing:.04em;
}
.po-card .po-meta {
    font-family:'JetBrains Mono',monospace; font-size:10px;
    color:#3a4560; margin-top:.25rem; line-height:1.8;
}
.po-card .po-reason {
    font-family:'JetBrains Mono',monospace; font-size:11px;
    color:#00e5cc; margin-top:.6rem; border-top:1px solid #101828;
    padding-top:.5rem; line-height:1.6;
}
</style>
"""

# ══════════════════════════════════════════════════════════════════
# SEED / MOCK DATA
# ══════════════════════════════════════════════════════════════════
PRODUCTS = [
    {"id":1,"product":"Laptop Pro 14",       "sku":"TECH-LP14","category":"Electronics","stock":8,  "reorder_point":15,"max_stock":100,"unit_cost":1200,"supplier":"TechCorp Asia","lead_days":14},
    {"id":2,"product":"USB-C Hub 7-Port",    "sku":"TECH-HUB7","category":"Electronics","stock":42, "reorder_point":20,"max_stock":200,"unit_cost":45,  "supplier":"GadgetWorld",  "lead_days":7},
    {"id":3,"product":"Ergo Office Chair",   "sku":"FURN-OC01","category":"Furniture",  "stock":5,  "reorder_point":10,"max_stock":50, "unit_cost":380, "supplier":"FurnCo EU",    "lead_days":21},
    {"id":4,"product":"Standing Desk 160",   "sku":"FURN-SD16","category":"Furniture",  "stock":27, "reorder_point":8, "max_stock":60, "unit_cost":650, "supplier":"FurnCo EU",    "lead_days":21},
    {"id":5,"product":"Webcam 4K Pro",       "sku":"TECH-WC4K","category":"Electronics","stock":63, "reorder_point":25,"max_stock":150,"unit_cost":180, "supplier":"TechCorp Asia","lead_days":10},
    {"id":6,"product":"Mechanical Keyboard", "sku":"TECH-KB01","category":"Electronics","stock":11, "reorder_point":20,"max_stock":100,"unit_cost":140, "supplier":"KeyMaster Inc","lead_days":8},
    {"id":7,"product":"27\" 4K Monitor",     "sku":"TECH-MN27","category":"Electronics","stock":3,  "reorder_point":10,"max_stock":80, "unit_cost":750, "supplier":"ScreenTech",   "lead_days":12},
    {"id":8,"product":"LED Desk Lamp",       "sku":"FURN-DL01","category":"Furniture",  "stock":89, "reorder_point":15,"max_stock":200,"unit_cost":60,  "supplier":"BrightGoods",  "lead_days":5},
]

RISK_INCIDENTS = [
    {"date":"2024-01-15","supplier":"TechCorp Asia","incident":"Port congestion Shenzhen — 8-day delay","severity":"high"},
    {"date":"2024-02-03","supplier":"FurnCo EU",    "incident":"Rotterdam dock strike — 12-day delay","severity":"high"},
    {"date":"2024-03-20","supplier":"GadgetWorld",  "incident":"Raw material shortage, +4% cost increase","severity":"medium"},
    {"date":"2024-04-10","supplier":"ScreenTech",   "incident":"Freight rate spike +22% (Q2 peak)","severity":"medium"},
    {"date":"2024-05-05","supplier":"KeyMaster Inc","incident":"Factory audit delay, 3-day hold","severity":"low"},
    {"date":"2024-06-18","supplier":"TechCorp Asia","incident":"Typhoon Mawar — Guangzhou port closure 5 days","severity":"high"},
    {"date":"2024-07-22","supplier":"FurnCo EU",    "incident":"Driver shortage UK — last-mile delay +4 days","severity":"medium"},
    {"date":"2024-08-09","supplier":"BrightGoods",  "incident":"Component substitution, minor quality flag","severity":"low"},
]


def _make_history(product_id: int, days: int = 120) -> pd.DataFrame:
    """
    Synthetic daily sales — weekly seasonality + trend + noise.
    Mimics a Kaggle retail POS dataset sample.
    """
    random.seed(product_id * 13)
    base = 7 + product_id * 2
    rows = []
    for i in range(days):
        date   = datetime.now().date() - timedelta(days=days - i)
        trend  = 1 + 0.003 * i
        wday   = date.weekday()
        season = 1.35 if wday < 2 else (0.65 if wday >= 5 else 1.0)
        noise  = random.gauss(0, 1.5)
        qty    = max(1, round(base * trend * season + noise))
        rows.append({"ds": pd.Timestamp(date), "y": qty})
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════
# API HELPERS  — cached, fall back to mock data when offline
# ══════════════════════════════════════════════════════════════════

def backend_alive() -> bool:
    try:
        return requests.get(f"{API_BASE}/health", timeout=2).status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=30)
def api_inventory() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE}/inventory", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return PRODUCTS


@st.cache_data(ttl=60)
def api_weather() -> dict:
    try:
        r = requests.get(f"{API_BASE}/weather", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {"icon":"⛅","city":"Demo City","temp":24,
                "condition":"Partly Cloudy","source":"mock"}


@st.cache_data(ttl=30)
def api_history(product_id: int) -> pd.DataFrame:
    try:
        r = requests.get(
            f"{API_BASE}/sales-history?product_id={product_id}&days=120",
            timeout=5)
        r.raise_for_status()
        df = pd.DataFrame(r.json())
        df["ds"] = pd.to_datetime(df["sale_date"])
        df["y"]  = df["qty_sold"].astype(int)
        return df[["ds","y"]].sort_values("ds").reset_index(drop=True)
    except Exception:
        return _make_history(product_id)


@st.cache_data(ttl=30)
def api_purchase_orders() -> list[dict]:
    try:
        r = requests.get(f"{API_BASE}/purchase-orders", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def api_agent_query(user_message: str, history: list[dict]) -> str:
    """
    POST /agent/query  — sends message to LangChain ReAct agent.
    Falls back to a canned chain-of-thought response if offline.
    """
    try:
        payload = {"message": user_message, "history": history}
        r = requests.post(f"{API_BASE}/agent/query", json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("response", "No response from agent.")
    except Exception:
        return _mock_agent_response(user_message)


def _mock_agent_response(msg: str) -> str:
    msg_l = msg.lower()
    if any(w in msg_l for w in ["reorder","po","order","purchase","stock low","stockout"]):
        return (
            "**Agent Reasoning (Chain-of-Thought):**\n\n"
            "1. **Checked inventory** → Laptop Pro 14 has 8 units on hand.\n"
            "2. **Ran forecast** → Prophet predicts avg demand of 3.2 units/day "
            "over next 14 days = ~45 units needed.\n"
            "3. **Calculated ROP** → Lead time 14 days × daily demand 3.2 = ROP 45. "
            "Current stock (8) < ROP (45). ⚠ Trigger fired.\n"
            "4. **Calculated EOQ** → √(2 × 45 × 1200 / 0.20) ≈ **735 units** optimal "
            "order quantity (capped at max_stock 100).\n\n"
            "**Draft Purchase Order Generated:**\n"
            "- Product: Laptop Pro 14\n"
            "- Supplier: TechCorp Asia\n"
            "- Quantity: 50 units\n"
            "- Est. Cost: $60,000\n"
            "- Lead Time: 14 days\n\n"
            "*Awaiting human approval.*"
        )
    if any(w in msg_l for w in ["risk","delay","supplier","weather"]):
        return (
            "**Risk Intelligence (RAG retrieval):**\n\n"
            "Found 3 relevant historical incidents for **TechCorp Asia**:\n\n"
            "- Jan 2024: Port congestion Shenzhen — 8-day delay (HIGH)\n"
            "- Jun 2024: Typhoon Mawar — Guangzhou port closure 5 days (HIGH)\n\n"
            "**Recommendation:** Current weather in Shenzhen shows storm system "
            "within 400km. Historical similarity score: 0.82.\n"
            "Suggest pre-ordering by +7 days buffer on lead time."
        )
    if any(w in msg_l for w in ["forecast","demand","predict","prophet"]):
        return (
            "**Forecast Summary:**\n\n"
            "Running Prophet on 120-day sales history.\n\n"
            "- Avg daily demand (next 30d): **3.2 units/day**\n"
            "- Peak expected: **Tuesday Mar 18** (weekly seasonality peak)\n"
            "- 90% CI range: 1.8 – 4.6 units/day\n"
            "- Predicted stockout for Laptop Pro 14: **Mar 15** ⚠\n\n"
            "Recommend immediate reorder trigger."
        )
    return (
        "I'm the SupplyMind agent. I can help you with:\n\n"
        "- **Inventory checks** — 'What products are low on stock?'\n"
        "- **Demand forecasts** — 'Forecast Laptop Pro 14 for next 30 days'\n"
        "- **Purchase orders** — 'Generate a PO for low stock items'\n"
        "- **Risk intelligence** — 'What are the risks for TechCorp Asia?'\n\n"
        "What would you like to know?"
    )


# ══════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ══════════════════════════════════════════════════════════════════
PLOTLY_THEME = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="JetBrains Mono, monospace", color="#1e2d45", size=11),
    margin        = dict(l=10, r=10, t=38, b=10),
    xaxis         = dict(gridcolor="#0c1525", zeroline=False, showline=False,
                         tickfont=dict(size=10)),
    yaxis         = dict(gridcolor="#0c1525", zeroline=False, showline=False,
                         tickfont=dict(size=10)),
    legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#3a4560", size=10)),
    title         = dict(font=dict(family="Rajdhani, sans-serif", size=13,
                                   color="#6a7a9a"), x=0, xanchor="left"),
    hoverlabel    = dict(bgcolor="#080c1a", bordercolor="#101828",
                         font=dict(family="JetBrains Mono, monospace", size=11)),
)