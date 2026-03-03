"""
Blog API package.
Exports the blog API blueprint for registration with the Flask app.
"""
from app.api.v1.blog.routes import blog_api_bp

__all__ = ['blog_api_bp']
