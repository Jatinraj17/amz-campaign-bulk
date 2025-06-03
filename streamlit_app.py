"""
Streamlit entry point for the Amazon Ads Bulk Campaign Generator.
Run this file using: streamlit run streamlit_app.py
"""
""" New login Code for wordpress"""
import streamlit as st
import jwt

SECRET_KEY = "y0uRs3cR3tK3y!$%A9zX81#^dFgjLk2mN8R"  # Same as WordPress

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        st.error("Session expired. Please login again.")
        st.stop()
    except jwt.InvalidTokenError:
        st.error("Invalid token. Access denied.")
        st.stop()

def get_token_from_query():
    query_params = st.query_params
    token = query_params.get("token", [None])[0]
    return token

# Main logic
token = get_token_from_query()
if not token:
    st.error("Access denied. No token provided.")
    st.stop()

user_id = validate_token(token)
st.success(f"Authenticated as WordPress user ID: {user_id}")

"""new login code ends"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Create necessary directories
os.makedirs('templates', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Import and run the app
from amazon_bulk_generator.web.app import BulkCampaignApp

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()
