"""
Streamlit entry point for the Amazon Ads Bulk Campaign Generator.
Run this file using: streamlit run streamlit_app.py
"""

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
