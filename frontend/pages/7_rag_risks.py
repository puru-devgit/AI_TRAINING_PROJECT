import streamlit as st
import requests

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #0a0e1a 0%, #0d1117 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1117 0%, #161b22 100%); border-right: 1px solid #21262d; }
.page-title { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #f85149, #d29922); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.risk-card {
    background: linear-gradient(135deg, #1c1a1a, #2d1f1f);
    border: 1px solid #3d2020; border-left: 4px solid #f85149;
    border-radius: 12px; padding: 16px 20px; margin: 10px 0;
}
.risk-score { font-size: 0.75rem; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }
.risk-text { color: #ffa198; font-size: 0.95rem; margin-top: 6px; line-height: 1.5; }
.score-bar { height: 4px; border-radius: 2px; background: linear-gradient(90deg, #f85149, #d29922); margin-top: 10px; }
.preset-btn { background: linear-gradient(135deg, #161b22, #1c2128); border: 1px solid #30363d; border-radius: 10px; padding: 10px 14px; cursor: pointer; transition: all 0.2s; }
.section-label { font-size: 0.75rem; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin: 16px 0 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-title">⚠️ RAG Risk Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#8b949e;margin-bottom:20px">FAISS vector search · sentence-transformers · 50+ supply chain incident corpus</div>', unsafe_allow_html=True)

# Preset queries
st.markdown('<div class="section-label">🔍 Preset Risk Queries</div>', unsafe_allow_html=True)
PRESETS = [
    ("🌾", "Rice & Grain Risks",        "rice wheat grain supply disruption"),
    ("🛢️", "Oil Supply Risks",           "cooking oil palm olive supply shortage"),
    ("☕", "Beverage & Coffee Risks",    "coffee tea beverage supply chain"),
    ("🚢", "Logistics & Shipping Risks", "shipping logistics freight delay"),
    ("🏭", "Supplier & Manufacturing",   "supplier factory manufacturing quality"),
    ("💄", "Skincare & Haircare Risks",  "skincare haircare cosmetic supply"),
    ("🌍", "Geopolitical Risks",         "trade tariff geopolitical currency"),
    ("📈", "Demand Surge Risks",         "demand surge stockout festive season"),
]

preset_query = None
cols = st.columns(4)
for i, (icon, label, query) in enumerate(PRESETS):
    with cols[i % 4]:
        if st.button(f"{icon} {label}", key=f"preset_{i}", use_container_width=True):
            preset_query = query

st.markdown("---")

# Custom query
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Enter risk query", value=preset_query or "supply chain disruption",
                          placeholder="e.g. coffee shortage, shipping delay, supplier quality...")
with col2:
    top_k = st.selectbox("Results", [3, 5, 8, 10], index=1)

if st.button("🔍 Search Risk Intelligence", type="primary", use_container_width=True) or preset_query:
    with st.spinner("Searching FAISS vector index..."):
        try:
            r = requests.get(f"http://localhost:8000/risks/",
                             params={"query": query, "top_k": top_k}, timeout=15)
            data = r.json()
        except Exception as e:
            st.error(f"Backend error: {e}")
            st.stop()

    results = data.get("results", [])
    st.markdown(f'<div style="color:#8b949e;margin:12px 0">Found <strong style="color:#e6edf3">{len(results)}</strong> relevant incidents for: <em style="color:#58a6ff">"{query}"</em></div>', unsafe_allow_html=True)

    for i, res in enumerate(results):
        score = res["relevance_score"]
        score_pct = int(score * 100)
        color = "#f85149" if score > 0.6 else ("#d29922" if score > 0.4 else "#8b949e")
        st.markdown(f"""
        <div class="risk-card">
            <div class="risk-score">#{i+1} &nbsp;·&nbsp; Relevance Score: <span style="color:{color}">{score:.3f} ({score_pct}%)</span></div>
            <div class="risk-text">{res['incident']}</div>
            <div class="score-bar" style="width:{score_pct}%"></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-label">🧠 How RAG Risk Intelligence Works</div>', unsafe_allow_html=True)
st.markdown("""
<div style="background:linear-gradient(135deg,#161b22,#1c2128);border:1px solid #30363d;border-radius:12px;padding:20px;color:#c9d1d9;line-height:1.8">
<strong style="color:#58a6ff">1. Corpus</strong> — 50+ real-world supply chain incident descriptions across grains, oils, beverages, logistics, suppliers, and geopolitics<br>
<strong style="color:#a371f7">2. Embeddings</strong> — Each incident encoded into a 384-dim vector using <code>sentence-transformers/all-MiniLM-L6-v2</code><br>
<strong style="color:#3fb950">3. FAISS Index</strong> — Vectors stored in a flat inner-product index for fast cosine similarity search<br>
<strong style="color:#d29922">4. Query</strong> — Your query is embedded and matched against the corpus to retrieve the most semantically similar incidents<br>
<strong style="color:#f78166">5. Agent Integration</strong> — The LangChain ReAct agent calls this as a tool to inform purchase order decisions
</div>
""", unsafe_allow_html=True)
