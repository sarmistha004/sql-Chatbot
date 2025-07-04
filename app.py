import streamlit as st

# Set the page config
st.set_page_config(page_title="DataWhiz", layout="centered")

# Redirect immediately to the login page
st.markdown("""
    <meta http-equiv="refresh" content="0; url=/?page=1_Login" />
""", unsafe_allow_html=True)
