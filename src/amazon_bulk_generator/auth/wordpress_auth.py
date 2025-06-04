"""
WordPress JWT Authentication module
"""
import os
import jwt
import streamlit as st

class WordPressAuth:
    def __init__(self):
        self.wp_url = "https://ecommercean.com"
        self.login_url = "https://ecommercean.com/log-in/"
        self.secret_key = "y0uRs3cR3tK3y!$%A9zX81#^dFgjLk2mN8R"

    def check_auth(self) -> bool:
        """Check if user is authenticated"""
        # Get token from URL parameters if present
        query_params = st.query_params
        token = query_params.get("token")
        
        if token:
            try:
                # Validate JWT token
                payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
                st.session_state.wp_token = token
                st.session_state.user_id = payload.get("user_id")
                return True
            except jwt.ExpiredSignatureError:
                st.error("Session expired. Please login again.")
                return False
            except jwt.InvalidTokenError:
                st.error("Invalid token. Access denied.")
                return False
        
        return 'wp_token' in st.session_state

    def logout(self):
        """Clear authentication state"""
        if 'wp_token' in st.session_state:
            del st.session_state.wp_token
        if 'user_id' in st.session_state:
            del st.session_state.user_id

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
