import streamlit as st

st.set_page_config(
    page_title="AI Supply Chain",
    layout="wide",
    page_icon="📦"
)

st.title("📦 AI Supply Chain Optimization Agent")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Forecast", "Inventory", "Agent Chat"]
)

if page == "Dashboard":
    import pages.dashboard
elif page == "Forecast":
    import pages.forecast
elif page == "Inventory":
    import pages.inventory
elif page == "Agent Chat":
    import pages.agent_chat