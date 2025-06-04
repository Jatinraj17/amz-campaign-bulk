"""
Streamlit entry point for the Amazon Ads Bulk Campaign Generator.
Run this file using: streamlit run streamlit_app.py
"""
import streamlit as st
import jwt
from pathlib import Path
import sys
import os

# ✅ Must be FIRST streamlit call
st.set_page_config(
    page_title="Amazon Ads Bulk Campaign Generator",
    page_icon="🎯",
    layout="wide"
)

# 🔐 Validate token from query
SECRET_KEY = "y0uRs3cR3tK3y!$%A9zX81#^dFgjLk2mN8R"  # Match with WordPress

def validate_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        st.error("❌ Session expired. Please login again from WordPress.")
        st.stop()
    except jwt.InvalidTokenError as e:
        st.error(f"❌ Token validation failed: {str(e)}")
        st.stop()

# ✅ Extract token safely from query
params = st.query_params
raw_token = params.get("token")
if not raw_token:
    st.error("❌ No token provided in URL. Please login from WordPress.")
    st.stop()

token = raw_token[0] if isinstance(raw_token, list) else raw_token
user_id = validate_token(token)
if not user_id:
    st.error("❌ Invalid token. Access denied.")
    st.stop()

st.success(f"✅ Authenticated as WordPress User ID: {user_id}")

# 🔄 Add src folder to path
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# 📂 Create necessary folders
os.makedirs('templates', exist_ok=True)
os.makedirs('output', exist_ok=True)

# ▶️ Launch app
from amazon_bulk_generator.web.app import BulkCampaignApp

app = BulkCampaignApp()
app.run()
