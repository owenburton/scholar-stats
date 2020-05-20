import streamlit as st

st.title("scholar stats")

url = st.text_input("copy/paste the url of a scholar profile from google scholars")

if url:
    