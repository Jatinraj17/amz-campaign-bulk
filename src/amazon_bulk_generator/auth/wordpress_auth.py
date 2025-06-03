"""
WordPress JWT Authentication module
"""
import os
import requests
from typing import Optional, Dict, Tuple
import streamlit as st

class WordPressAuth:
    def __init__(self):
        self.wp_url = "https://ecommercean.com"
        self.login_url = "https://ecommercean.com/log-in/"
        self.jwt_auth_url = f"{self.wp_url}/wp-json/jwt-auth/v1/token"
        self.validate_url = f"{self.wp_url}/wp-json/jwt-auth/v1/token/validate"

    def check_auth(self) -> bool:
        """Check if user is authenticated"""
        if 'wp_token' not in st.session_state:
            return False
        
        # Validate token with WordPress
        try:
            response = requests.post(
                self.validate_url,
                headers={'Authorization': f'Bearer {st.session_state.wp_token}'}
            )
            return response.status_code == 200
        except:
            return False

    def validate_token(self, token: str) -> bool:
        """Validate JWT token with WordPress"""
        try:
            response = requests.post(
                self.validate_url,
                headers={'Authorization': f'Bearer {token}'}
            )
            return response.status_code == 200
        except:
            return False

    def handle_oauth_callback(self, token: str) -> bool:
        """Handle OAuth callback and validate token"""
        if self.validate_token(token):
            st.session_state.wp_token = token
            return True
        return False

    def logout(self):
        """Clear authentication state"""
        if 'wp_token' in st.session_state:
            del st.session_state.wp_token

    def get_login_url(self) -> str:
        """Get WordPress login URL"""
        # Add return URL parameter to redirect back to the app after login
        return_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')
        return f"{self.login_url}?redirect_to={return_url}"

    def show_login_page(self):
        """Display login page with WordPress redirect"""
        st.title("Login Required")
        st.write("Please log in with your WordPress account to continue.")
        
        login_url = self.get_login_url()
        
        # Center the login button using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                f'<div style="text-align: center;">'
                f'<a href="{login_url}" target="_self">'
                '<button style="background-color: #FF4B4B; color: white; padding: 10px 20px; '
                'border: none; border-radius: 5px; cursor: pointer; width: 100%;">'
                'Login with WordPress</button></a></div>',
                unsafe_allow_html=True
            )
