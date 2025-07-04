import streamlit as st

# 🧑‍💻 Dummy credentials — you can later fetch from MySQL
users = {
    "Sarmistha Sen": "sarmistha@123",
    "Dr. Surajit Sen": "surajit@123",
    "Mithu Sen": "mithu@123"
}

# ✅ Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

def login():
    st.set_page_config(page_title="Login | DataWhiz", layout="centered")
    st.title("🔐 Login to DataWhiz")

    st.markdown("### Please enter your credentials:")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"✅ Welcome, {username}!")
            st.experimental_rerun()  # Refresh the session for new state
        else:
            st.error("❌ Invalid credentials. Please try again.")

# ✅ Control login access
if not st.session_state.logged_in:
    login()
else:
    st.success(f"✅ You are logged in as **{st.session_state.user}**")
    st.page_link("pages/2_Chatbot.py", label="Go to Chatbot 💬", icon="💡")

