"""
Authentication forms using Flask-WTF.
These forms handle user input validation for registration and login.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
    Regexp
)
from app.models import User


class RegistrationForm(FlaskForm):
    """
    User registration form.
    Validates username, email, and password with confirmation.
    """

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=80, message='Username must be between 3 and 80 characters'),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message='Username must contain only letters, numbers, and underscores'
            )
        ],
        render_kw={'placeholder': 'Enter username', 'class': 'form-control'}
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=120, message='Email must not exceed 120 characters')
        ],
        render_kw={'placeholder': 'Enter email', 'class': 'form-control', 'type': 'email'}
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=8, message='Password must be at least 8 characters long')
        ],
        render_kw={'placeholder': 'Enter password', 'class': 'form-control'}
    )

    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm password', 'class': 'form-control'}
    )

    submit = SubmitField('Register', render_kw={'class': 'btn btn-primary btn-block'})

    @staticmethod
    def validate_username(username):
        """
        Custom validator to check if username already exists.
        Raises ValidationError if username is taken.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    @staticmethod
    def validate_email(email):
        """
        Custom validator to check if email already exists.
        Raises ValidationError if email is already registered.
        """
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')


class LoginForm(FlaskForm):
    """
    User login form.
    Supports login with either username or email.
    """

    username_or_email = StringField(
        'Username or Email',
        validators=[
            DataRequired(message='Username or email is required'),
            Length(min=3, max=120, message='Must be between 3 and 120 characters')
        ],
        render_kw={'placeholder': 'Enter username or email', 'class': 'form-control'}
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required')
        ],
        render_kw={'placeholder': 'Enter password', 'class': 'form-control'}
    )

    remember_me = BooleanField(
        'Remember Me',
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Login', render_kw={'class': 'btn btn-primary btn-block'})


class ChangePasswordForm(FlaskForm):
    """
    Form for changing user password.
    Requires current password for verification.
    """

    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required')
        ],
        render_kw={'placeholder': 'Enter current password', 'class': 'form-control'}
    )

    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required'),
            Length(min=8, message='Password must be at least 8 characters long')
        ],
        render_kw={'placeholder': 'Enter new password', 'class': 'form-control'}
    )

    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password'),
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm new password', 'class': 'form-control'}
    )

    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'})
