"""
Streamlit entry point for the Amazon Ads Bulk Campaign Generator.
Run this file using: streamlit run streamlit_app.py
"""
import os
import sys
from pathlib import Path
import streamlit as st
import jwt

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="Amazon Bulk Campaign Generator", layout="wide")

# ✅ Secret must match WordPress
SECRET_KEY = "y0uRs3cR3tK3y!$%A9zX81#^dFgjLk2mN8R"

# ✅ Token handling
def get_token_from_query():
    query_params = st.query_params
    token = query_params.get("token", [None])[0]
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        st.error("❌ Session expired. Please login again from WordPress.")
        st.stop()
    except jwt.DecodeError:
        st.error("❌ Malformed token. Access denied.")
        st.stop()
    except jwt.InvalidTokenError:
        st.error("❌ Invalid token. Access denied.")
        st.stop()

# ✅ Check token before loading app
token = get_token_from_query()
if not token:
    st.error("❌ Access denied. No token provided.")
    st.stop()

user_id = validate_token(token)
st.success(f"✅ Authenticated as WordPress user ID: {user_id}")

# ✅ Setup environment (after validation)
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

os.makedirs('templates', exist_ok=True)
os.makedirs('output', exist_ok=True)

# ✅ Import and run app AFTER auth passes
from amazon_bulk_generator.web.app import BulkCampaignApp

if __name__ == "__main__":
    app = BulkCampaignApp()
    app.run()

