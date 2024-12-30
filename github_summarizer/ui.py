# Streamlit App Code
import streamlit as st
import os
from repo import get_repo_algo

st.title("GitHub Repository Analyzer")

repo_url = st.text_input("Enter GitHub Repository URL:")

if repo_url:
    st.write("Fetching repository details (it will take couple of minutes)...")
    algo_description, directory_structure = get_repo_algo(repo_url)

    st.text_area("Directory Structure", directory_structure, height=300)
    
    st.markdown("### Algorithm Description")
    st.markdown(algo_description)