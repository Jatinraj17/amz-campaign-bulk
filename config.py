"""
Configuration settings for the Amazon Bulk Campaign Generator
"""
import os

# WordPress Configuration
WORDPRESS_URL = "https://ecommercean.com"
WORDPRESS_LOGIN_URL = "https://ecommercean.com/log-in/"

# JWT Authentication URLs
JWT_AUTH_URL = f"{WORDPRESS_URL}/wp-json/jwt-auth/v1/token"
JWT_VALIDATE_URL = f"{WORDPRESS_URL}/wp-json/jwt-auth/v1/token/validate"

# App Configuration
APP_URL = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:10000')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Security
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-here')
