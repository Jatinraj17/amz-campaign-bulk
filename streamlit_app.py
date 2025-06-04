"""
Streamlit entry point for the Amazon Ads Bulk Campaign Generator.
Run this file using: streamlit run streamlit_app.py
"""
import streamlit as st
from pathlib import Path
import sys
import os

# ✅ Must be FIRST streamlit call
st.set_page_config(
    page_title="Amazon Ads Bulk Campaign Generator",
    page_icon="🎯",
    layout="wide"
)

# 🔄 Add src folder to path
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# 📂 Create necessary folders
os.makedirs('templates', exist_ok=True)
os.makedirs('output', exist_ok=True)

# ▶️ Launch app (authentication will be handled inside the app)
from amazon_bulk_generator.web.app import BulkCampaignApp

app = BulkCampaignApp()
app.run()
