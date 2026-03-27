import streamlit as st
from utils.api_clients import ask_agent

st.header("🤖 AI Supply Chain Agent")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask something about inventory...")

if st.button("Send"):
    if user_input:
        response = ask_agent(user_input)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Agent", response.get("response", "")))

# Display chat
for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Agent:** {msg}")