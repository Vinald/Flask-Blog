"""
Application error handlers.

Provides centralized error handling for the Flask application.
Includes custom error pages and API error responses.
"""
from flask import Blueprint, render_template, request, jsonify

errors_bp = Blueprint('errors', __name__)


def is_api_request():
    """Check if the request is for the API (expects JSON response)."""
    return (
        request.path.startswith('/api/') or 
        request.accept_mimetypes.best == 'application/json'
    )


@errors_bp.app_errorhandler(400)
def bad_request_error(error):
    """Handle 400 Bad Request errors."""
    if is_api_request():
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
        }), 400
    return render_template('errors/400.html', title='Bad Request'), 400


@errors_bp.app_errorhandler(401)
def unauthorized_error(error):
    """Handle 401 Unauthorized errors."""
    if is_api_request():
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    return render_template('errors/401.html', title='Unauthorized'), 401


@errors_bp.app_errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors."""
    if is_api_request():
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    return render_template('errors/403.html', title='Forbidden'), 403


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    if is_api_request():
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    return render_template('errors/404.html', title='Page Not Found'), 404


@errors_bp.app_errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 Method Not Allowed errors."""
    if is_api_request():
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'The {request.method} method is not allowed for this endpoint'
        }), 405
    return render_template('errors/405.html', title='Method Not Allowed'), 405


@errors_bp.app_errorhandler(429)
def too_many_requests_error(error):
    """Handle 429 Too Many Requests errors."""
    if is_api_request():
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429
    return render_template('errors/429.html', title='Too Many Requests'), 429


@errors_bp.app_errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    # Log the error in production
    if is_api_request():
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    return render_template('errors/500.html', title='Server Error'), 500


@errors_bp.app_errorhandler(503)
def service_unavailable_error(error):
    """Handle 503 Service Unavailable errors."""
    if is_api_request():
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable'
        }), 503
    return render_template('errors/503.html', title='Service Unavailable'), 503
