import streamlit as st

# ✅ Dummy user credentials
users = {
    "Sarmistha Sen": "sarmistha@123",
    "Dr. Surajit Sen": "surajit@123",
    "Mithu Sen": "mithu@123"
}

# ✅ Page config
st.set_page_config(page_title="Login | DataWhiz", page_icon="🔐", layout="centered")

# ✅ Session Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ✅ Login Form
def login():
    st.markdown("<h1 style='text-align:center;'>🔐 Login to <span style='color:#6C63FF;'>DataWhiz</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:20px;'>Your intelligent SQL assistant at your fingertips 💡</p>", unsafe_allow_html=True)

    st.write("")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_btn = st.button("Login", type="primary")

    if login_btn:
        if username in users and users[username] == password:
            st.success(f"✅ Welcome {username}!")
            st.session_state.logged_in = True
            st.session_state.user = username
            st.experimental_rerun()  # rerun to trigger switch_page
        else:
            st.error("❌ Invalid username or password")

# ✅ Login gate
if not st.session_state.logged_in:
    login()
else:
    st.switch_page("pages/2_Chatbot.py")
