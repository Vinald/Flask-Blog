"""
Authentication JSON API routes.
Returns JSON responses for Swagger UI documentation and API consumers.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user, logout_user
from app.services.auth_service import AuthService

# JSON API blueprint at /api/v1/auth
auth_api_bp = Blueprint('auth_api', __name__, url_prefix='/api/v1/auth')


@auth_api_bp.route('/register', methods=['POST'])
def register():
    """
    Register a New User
    Create a new user account with username, email, and password.
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              description: Desired username (must be unique)
              example: johndoe
            email:
              type: string
              description: Email address (must be unique)
              example: john@example.com
            password:
              type: string
              description: Password (minimum 8 characters)
              example: SecurePass123
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Account created successfully
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
      400:
        description: Validation error or duplicate user
        schema:
          type: object
          properties:
            error:
              type: string
              example: Username already exists
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user, error = AuthService.register_user(username, email, password)

    if user:
        return jsonify({
            'message': 'Account created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }), 201
    else:
        return jsonify({'error': error}), 400


@auth_api_bp.route('/login', methods=['POST'])
def login():
    """
    User Login
    Authenticate with username/email and password. Returns a session cookie.
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username_or_email
            - password
          properties:
            username_or_email:
              type: string
              description: Username or email address
              example: johndoe
            password:
              type: string
              description: Account password
              example: SecurePass123
            remember_me:
              type: boolean
              description: Whether to remember the login session
              default: false
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid username/email or password
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    username_or_email = data.get('username_or_email', '').strip()
    password = data.get('password', '')
    remember = data.get('remember_me', False)

    if not username_or_email or not password:
        return jsonify({'error': 'Username/email and password are required'}), 400

    success, error = AuthService.authenticate_user(username_or_email, password, remember)

    if success:
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': current_user.id,
                'username': current_user.username,
            }
        }), 200
    else:
        return jsonify({'error': error}), 401


@auth_api_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    User Logout
    End the current user session and clear the session cookie.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    produces:
      - application/json
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Logged out successfully
      401:
        description: User is not logged in
    """
    username = current_user.username
    AuthService.logout_user()
    return jsonify({'message': f'Goodbye, {username}! Logged out successfully'}), 200


@auth_api_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """
    Get User Profile
    Retrieve the current authenticated user's profile information.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    produces:
      - application/json
    responses:
      200:
        description: User profile data
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
            is_active:
              type: boolean
            is_admin:
              type: boolean
            created_at:
              type: string
              format: date-time
            last_login:
              type: string
              format: date-time
            post_count:
              type: integer
      401:
        description: User is not logged in
    """
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'is_active': current_user.is_active,
        'is_admin': current_user.is_admin,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
        'post_count': len(current_user.posts),
    }), 200


@auth_api_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change Password
    Change the current user's password. Requires current password for verification.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              description: Current password for verification
            new_password:
              type: string
              description: New password (minimum 8 characters)
    responses:
      200:
        description: Password changed successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password changed successfully
      400:
        description: Validation error
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: User is not logged in
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400

    success, error = AuthService.change_password(current_user, current_password, new_password)

    if success:
        return jsonify({'message': 'Password changed successfully'}), 200
    else:
        return jsonify({'error': error}), 400


@auth_api_bp.route('/account/deactivate', methods=['POST'])
@login_required
def deactivate_account():
    """
    Deactivate Account
    Deactivate the current user's account. The account is not deleted but marked
    as inactive. Contact support to reactivate.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    produces:
      - application/json
    responses:
      200:
        description: Account deactivated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Account deactivated successfully
      400:
        description: Failed to deactivate account
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: User is not logged in
    """
    success, error = AuthService.deactivate_user(current_user)

    if success:
        logout_user()
        return jsonify({'message': 'Account deactivated successfully. Contact support to reactivate.'}), 200
    else:
        return jsonify({'error': error}), 400
