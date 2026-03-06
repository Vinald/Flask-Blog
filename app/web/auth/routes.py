"""
Authentication web views - handles all authentication HTML routes.
Includes registration, login, logout, and password management.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm, UpdateProfileForm
from app.services.auth_service import AuthService
from app.utils import save_profile_image
from urllib.parse import urlparse

# Create authentication web blueprint
# url_prefix='/auth' for HTML routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User Registration (HTML)
    Register a new user account with username, email, and password.
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
    """

    # Get username before logging out
    username = current_user.username

    # Call service layer to logout
    AuthService.logout_user()

    flash(f'Goodbye, {username}! You have been logged out.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User Profile
    Display the current user's profile information and account details.
    Also handles profile updates including profile image upload.
    """
    form = UpdateProfileForm()

    # Handle form submission (profile update)
    if form.validate_on_submit():
        # Check if user uploaded a profile image
        if form.profile_image.data:
            # Save the uploaded image
            filename, error = save_profile_image(form.profile_image.data, current_user.id)

            if filename:
                # Update user's profile image in database
                success, error = AuthService.update_profile_image(current_user, filename)

                if success:
                    flash('Profile image updated successfully!', 'success')
                else:
                    flash(f'Failed to update profile image: {error}', 'danger')
            else:
                flash(f'Failed to upload image: {error}', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', title='Profile', user=current_user, form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change the current user's password. Requires current password verification.
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


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def request_password_reset():
    """
    Request Password Reset
    Allow users to request a password reset link via email.
    """
    # Redirect authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    from app.forms import RequestPasswordResetForm
    form = RequestPasswordResetForm()

    if form.validate_on_submit():
        email = form.email.data

        # Request password reset
        success, message, token = AuthService.request_password_reset(email)

        if success and token:
            # Get user and send reset email
            user = AuthService.get_user_by_email(email)
            if user:
                from app.utils.email import send_password_reset_email
                reset_url = url_for('auth.reset_password', token=token, _external=True)

                if send_password_reset_email(user, reset_url):
                    flash(message, 'info')
                else:
                    flash('Failed to send reset email. Please try again later.', 'danger')
            else:
                # User not found but still show generic message for security
                flash(message, 'info')
        else:
            # Show generic message for security
            flash(message, 'info' if success else 'danger')

        return redirect(url_for('auth.login'))

    return render_template('auth/request_reset.html', form=form, title='Reset Password')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset Password with Token
    Allow users to reset their password using a valid reset token.
    """
    # Redirect authenticated users
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    from app.forms import ResetPasswordForm
    form = ResetPasswordForm()

    if form.validate_on_submit():
        new_password = form.password.data

        # Reset password
        success, error = AuthService.reset_password(token, new_password)

        if success:
            flash('Your password has been reset successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')
            return redirect(url_for('auth.request_password_reset'))

    return render_template('auth/reset_password.html', form=form, token=token, title='Reset Password')


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
