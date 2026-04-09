import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")


with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()
# st.html(html_content, unsafe_allow_javascript =True)
components.html(html_content, width= 5000, height = 2000, scrolling=True)