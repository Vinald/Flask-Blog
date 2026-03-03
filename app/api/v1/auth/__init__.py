"""
Authentication API package.
Exports the authentication API blueprint for registration with the Flask app.
"""
from app.api.v1.auth.routes import auth_api_bp

__all__ = ['auth_api_bp']
