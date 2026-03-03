"""
API v1 package.
Combines all v1 API blueprints into a single parent blueprint.
"""
from flask import Blueprint
from app.api.v1.auth import auth_api_bp
from app.api.v1.blog import blog_api_bp

# Create parent API v1 blueprint (optional - for future use if you want nested blueprints)
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

__all__ = ['api_v1_bp', 'auth_api_bp', 'blog_api_bp']
