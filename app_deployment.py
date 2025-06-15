# AWS Amplify deployment wrapper
import streamlit as st
import os
import sys

# Set Streamlit configuration for deployment
st.set_page_config(
    page_title="AI Blackjack Trainer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import and run the main application
if __name__ == "__main__":
    # Import main app
    exec(open('app.py').read())