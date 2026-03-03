"""
Web (HTML) blueprints package.
Contains all HTML-based routes for the Flask Blog application.
"""
from app.web.main import main_bp
from app.web.auth import auth_bp
from app.web.blog import blog_bp

__all__ = ['main_bp', 'auth_bp', 'blog_bp']
