import streamlit as st
from utils.api_clients import ask_agent

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #a371f7, #f78166); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

.example-card {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid #30363d; border-radius: 12px;
    padding: 14px 16px; cursor: pointer;
    transition: all 0.2s; margin-bottom: 8px;
}
.example-card:hover { border-color: #a371f7; background: linear-gradient(135deg, #1c2128, #21262d); }
.example-icon { font-size: 1.3rem; margin-bottom: 6px; }
.example-title { font-size: 0.85rem; font-weight: 600; color: #e6edf3; margin-bottom: 4px; }
.example-desc { font-size: 0.75rem; color: #8b949e; line-height: 1.4; }

.chat-user {
    background: linear-gradient(135deg, #1f2d3d, #1c2d3d);
    border: 1px solid #1f6feb; border-radius: 12px 12px 4px 12px;
    padding: 12px 16px; margin: 8px 0; color: #c9d1d9;
}
.chat-bot {
    background: linear-gradient(135deg, #1a1f2e, #1c2128);
    border: 1px solid #30363d; border-radius: 12px 12px 12px 4px;
    padding: 12px 16px; margin: 8px 0; color: #c9d1d9;
    border-left: 3px solid #a371f7;
}
.section-label { font-size: 0.75rem; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 8px; }

[data-testid="stChatInput"] textarea {
    background: #161b22 !important; border: 1px solid #30363d !important;
    color: #e6edf3 !important; border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">🤖 AI Decision Agent</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">LangChain ReAct Agent · Inventory · Forecast · ROP/EOQ · Risk RAG · Auto PO Generation</div>', unsafe_allow_html=True)

# Example Questions
st.markdown('<div class="section-label">💡 Example Questions — Click to Ask</div>', unsafe_allow_html=True)

EXAMPLES = [
    {
        "icon": "📦",
        "title": "Check all stock levels",
        "desc": "Identify which products are below reorder point",
        "query": "Check inventory levels for all products and identify which ones need reordering."
    },
    {
        "icon": "📈",
        "title": "Forecast demand for Rice",
        "desc": "Run Prophet forecast and get 14-day demand prediction",
        "query": "Run a demand forecast for Rice and tell me the expected demand for the next 14 days."
    },
    {
        "icon": "🧮",
        "title": "Calculate ROP & EOQ for Coffee",
        "desc": "Get optimal reorder point and economic order quantity",
        "query": "Calculate the Reorder Point and Economic Order Quantity for Coffee Beans."
    },
    {
        "icon": "⚠️",
        "title": "Assess supply chain risks",
        "desc": "Retrieve RAG risk intelligence for current inventory",
        "query": "What are the current supply chain risks for Rice and Sugar? Retrieve relevant risk intelligence."
    },
    {
        "icon": "🛒",
        "title": "Generate POs for critical items",
        "desc": "Auto-create purchase orders for low stock products",
        "query": "Check which products are below their reorder point and generate purchase orders for them."
    },
    {
        "icon": "🔍",
        "title": "Full supply chain analysis",
        "desc": "End-to-end check: stock → forecast → ROP → risks → PO",
        "query": "Do a full supply chain analysis for Cooking Oil: check stock, forecast demand, calculate ROP/EOQ, assess risks, and generate a purchase order if needed."
    },
]

quick_query = None
cols = st.columns(3)
for i, ex in enumerate(EXAMPLES):
    with cols[i % 3]:
        if st.button(f"{ex['icon']} {ex['title']}", key=f"ex_{i}", use_container_width=True, help=ex["desc"]):
            quick_query = ex["query"]

st.markdown("---")

# Quick action buttons
st.markdown('<div class="section-label">⚡ Quick Actions</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
if col1.button("🔴 Critical Items Only", use_container_width=True):
    quick_query = "Which products are critically low on stock right now? List them with their current stock and reorder points."
if col2.button("💰 Best Supplier Analysis", use_container_width=True):
    quick_query = "Analyze suppliers for Rice and Coffee Beans. Which supplier offers the best price-to-reliability ratio?"
if col3.button("📊 Weekly Demand Summary", use_container_width=True):
    quick_query = "Give me a weekly demand summary for all products based on recent sales history."

st.markdown("---")

# Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f'<div class="chat-user">👤 <strong>You</strong><br>{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot">🤖 <strong>SupplyMind Agent</strong><br>{msg}</div>', unsafe_allow_html=True)

query = quick_query or st.chat_input("Ask about stock, demand, risks, or request a purchase order...")

if query:
    st.session_state.messages.append(("user", query))
    st.markdown(f'<div class="chat-user">👤 <strong>You</strong><br>{query}</div>', unsafe_allow_html=True)

    with st.spinner("🧠 Agent reasoning..."):
        result = ask_agent(query)

    if isinstance(result, dict) and "error" in result:
        response = f"Backend error: {result['error']}"
    else:
        response = result.get("response", str(result)) if isinstance(result, dict) else str(result)

    st.markdown(f'<div class="chat-bot">🤖 <strong>SupplyMind Agent</strong><br>{response}</div>', unsafe_allow_html=True)
    st.session_state.messages.append(("bot", response))

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()
