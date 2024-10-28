import streamlit as st


def show_sidebar(menu_name=""):
    with st.sidebar:
        st.header(menu_name)
