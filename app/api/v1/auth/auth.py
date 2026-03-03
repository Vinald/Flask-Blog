"""
Authentication blueprint - handles all authentication routes.
Includes registration, login, logout, and password management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm
from app.services.auth_service import AuthService
from urllib.parse import urlparse

# Create authentication blueprint
# url_prefix='/api/v1/auth' means all routes will be prefixed with /api/v1/auth
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration
    Register a new user account with username, email, and password.
    ---
    tags:
      - Authentication
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: Desired username (must be unique)
        example: johndoe
      - name: email
        in: formData
        type: string
        required: true
        description: Email address (must be unique)
        example: john@example.com
      - name: password
        in: formData
        type: string
        required: true
        description: Password (minimum 8 characters)
        example: SecurePass123
      - name: confirm_password
        in: formData
        type: string
        required: true
        description: Password confirmation (must match password)
        example: SecurePass123
    responses:
      200:
        description: Registration form displayed (GET) or validation error (POST)
      302:
        description: Redirect to login on success, or to home if already logged in
    """
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    # Process form submission
    if form.validate_on_submit():
        # Extract form data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Call service layer to register user
        user, error = AuthService.register_user(username, email, password)

        if user:
            # Registration successful
            flash(f'Account created successfully! Welcome, {user.username}. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Registration failed
            flash(f'Registration failed: {error}', 'danger')

    # Display registration form (GET request or validation failed)
    return render_template('auth/register.html', form=form, title='Register')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User Login
    Authenticate a user with username/email and password. Creates a session cookie.
    ---
    tags:
      - Authentication
    parameters:
      - name: username_or_email
        in: formData
        type: string
        required: true
        description: Username or email address
        example: johndoe
      - name: password
        in: formData
        type: string
        required: true
        description: Account password
        example: SecurePass123
      - name: remember_me
        in: formData
        type: boolean
        required: false
        description: Whether to remember the login session
        default: false
      - name: next
        in: query
        type: string
        required: false
        description: URL to redirect to after successful login
    responses:
      200:
        description: Login form displayed (GET) or invalid credentials (POST)
      302:
        description: Redirect to home (or 'next' URL) on success, or to home if already logged in
    """
    # If user is already authenticated, redirect to home
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('main.index'))

    form = LoginForm()

    # Process form submission
    if form.validate_on_submit():
        # Extract form data
        username_or_email = form.username_or_email.data
        password = form.password.data
        remember = form.remember_me.data

        # Call service layer to authenticate user
        success, error = AuthService.authenticate_user(username_or_email, password, remember)

        if success:
            # Login successful
            flash(f'Welcome back, {current_user.username}!', 'success')

            # Handle 'next' parameter for redirect after login
            # This allows users to be redirected to the page they were trying to access
            next_page = request.args.get('next')

            # Validate next_page to prevent open redirect vulnerability
            if next_page and urlparse(next_page).netloc == '':
                return redirect(next_page)
            else:
                return redirect(url_for('main.index'))
        else:
            # Login failed
            flash(error, 'danger')

    # Display login form (GET request or validation failed)
    return render_template('auth/login.html', form=form, title='Login')


@auth_bp.route('/logout')
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
    responses:
      302:
        description: Redirect to home page after successful logout
      401:
        description: User is not logged in
    """
    # Get username before logging out
    username = current_user.username

    # Call service layer to logout
    AuthService.logout_user()

    flash(f'Goodbye, {username}! You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """
    User Profile
    Display the current user's profile information and account details.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    responses:
      200:
        description: Profile page with user information
        schema:
          type: object
          properties:
            username:
              type: string
              description: The user's username
            email:
              type: string
              description: The user's email address
            is_active:
              type: boolean
              description: Whether the account is active
            created_at:
              type: string
              format: date-time
              description: Account creation timestamp
            last_login:
              type: string
              format: date-time
              description: Last login timestamp
      401:
        description: User is not logged in
    """
    return render_template('auth/profile.html', title='Profile', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change Password
    Change the current user's password. Requires current password verification.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    parameters:
      - name: current_password
        in: formData
        type: string
        required: true
        description: Current account password for verification
      - name: new_password
        in: formData
        type: string
        required: true
        description: New password (minimum 8 characters)
      - name: confirm_new_password
        in: formData
        type: string
        required: true
        description: New password confirmation (must match new_password)
    responses:
      200:
        description: Password change form (GET) or validation error (POST)
      302:
        description: Redirect to profile on success
      401:
        description: User is not logged in
    """
    form = ChangePasswordForm()

    # Process form submission
    if form.validate_on_submit():
        # Extract form data
        current_password = form.current_password.data
        new_password = form.new_password.data

        # Call service layer to change password
        success, error = AuthService.change_password(
            current_user,
            current_password,
            new_password
        )

        if success:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(f'Password change failed: {error}', 'danger')

    # Display password change form
    return render_template('auth/change_password.html', form=form, title='Change Password')


@auth_bp.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    """
    Deactivate Account
    Deactivate the current user's account. The account is not deleted but marked as inactive.
    Contact support to reactivate.
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    responses:
      302:
        description: Redirect to home on success, or to profile on failure
      401:
        description: User is not logged in
    """
    # Deactivate account
    success, error = AuthService.deactivate_user(current_user)

    if success:
        # Logout user after deactivation
        logout_user()
        flash('Your account has been deactivated. Contact support to reactivate.', 'info')
        return redirect(url_for('main.index'))
    else:
        flash(f'Failed to deactivate account: {error}', 'danger')
        return redirect(url_for('auth.profile'))


# Error handlers for authentication blueprint
@auth_bp.errorhandler(401)
def unauthorized(error):
    """
    Handle 401 Unauthorized errors.
    Redirects to login page with appropriate message.
    """
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login', next=request.url))


@auth_bp.errorhandler(403)
def forbidden(error):
    """
    Handle 403 Forbidden errors.
    User is authenticated but doesn't have permission.
    """
    flash('You do not have permission to access this page.', 'danger')
    return redirect(url_for('main.index'))
