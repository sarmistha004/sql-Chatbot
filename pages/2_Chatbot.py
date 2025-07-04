import streamlit as st

# Restrict access if not logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🚫 Please login first.")
    st.stop()
