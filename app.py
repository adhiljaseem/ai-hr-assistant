import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="HR Chatbot", page_icon="🤖", layout="centered")
st.title("🤖 HR Chatbot Assistant")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.page = 1
    st.session_state.match_buffer = []

# Add welcome message if first time
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I’m your **HR Assistant**.\n\nAsk me anything about employees, skills, availability, or who might be best for a project."
    })

# Sidebar with clear option
with st.sidebar:
    st.header("🧹 Chat Options")
    if st.button("Clear Chat History"):
        st.session_state.clear()
        st.rerun()  # ✅ New supported rerun method

# Display previous chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input field
if user_input := st.chat_input("Ask about employees, skills, or availability..."):
    # Show user message in chat
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send to FastAPI backend
                res = requests.post("http://localhost:8000/chat", json={"query": user_input}, timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("response", "No response")
                    matches = data.get("matches", [])

                    # Show assistant's reply
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    # Save results for optional display
                    st.session_state.match_buffer = matches
                    st.session_state.page = 1
                else:
                    error_msg = f"❌ API error: {res.status_code}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"🚨 Could not connect to backend: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Show matched employees (optional)
if st.session_state.match_buffer:
    with st.expander("👥 View Matched Employees", expanded=True):
        per_page = 5
        total = len(st.session_state.match_buffer)
        start = (st.session_state.page - 1) * per_page
        end = start + per_page

        for emp in st.session_state.match_buffer[start:end]:
            st.markdown(f"""
                **{emp['name']}** — *{emp['role']}*, `{emp['location']}`  
                • **Skills:** {', '.join(emp['skills'])}  
                • **Projects:** {', '.join(emp['current_projects'] + emp['past_projects'])}  
                • **Email:** {emp['email']} | **Phone:** {emp['phone_number']}  
                • **Manager:** {emp['manager_name']}  
                • **Availability:** {emp['availability_date']} | **Status:** {emp['employee_status']}  
                ---
            """)

        # Load More button if more results exist
        if end < total:
            if st.button("🔽 Load More"):
                st.session_state.page += 1
                st.rerun()
