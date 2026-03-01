"""
Authentication API package.
Exports the authentication blueprint for registration with the Flask app.
"""
from app.api.v1.auth.auth import auth_bp

__all__ = ['auth_bp']
