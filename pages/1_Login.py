import streamlit as st

# Dummy credentials (replace with your database check if needed)
users = {
    "Sarmistha Sen": "sarmistha@123",
    "Dr. Surajit Sen": "surajit@123",
    "Mithu Sen": "mithu@123"
}

def login():
    st.title("🔐 Login to DataWhiz")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome, {username}!")
            st.switch_page("pages/2_Chatbot.py")
        else:
            st.error("Invalid credentials. Try again.")

# Session initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.switch_page("pages/2_Chatbot.py")
