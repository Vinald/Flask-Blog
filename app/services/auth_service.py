"""
Authentication service layer.
Contains all business logic for user authentication, registration, and session management.
Separates business logic from routes for better maintainability and testing.
"""
from app.models import User
from app.extensions import db
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timezone
from typing import Optional, Tuple


class AuthService:
    """
    Service class for handling authentication operations.
    Provides methods for registration, login, logout, and password management.
    """

    @staticmethod
    def register_user(username: str, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user account.

        Args:
            username (str): Desired username
            email (str): User's email address
            password (str): Plain text password (will be hashed)

        Returns:
            Tuple[Optional[User], Optional[str]]: (User object, error message)
            Returns (User, None) on success, (None, error_message) on failure
        """
        # Normalize email to lowercase
        email = email.lower().strip()
        username = username.strip()

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, 'Username already exists'

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, 'Email already registered'

        try:
            # Create new user instance
            user = User(
                username=username,
                email=email,
                is_active=True,
                is_admin=False
            )
            # Set password (will be automatically hashed by the model)
            user.password = password

            # Save to database
            db.session.add(user)
            db.session.commit()

            return user, None

        except Exception as e:
            # Rollback on any error
            db.session.rollback()
            return None, f'Registration failed: {str(e)}'

    @staticmethod
    def authenticate_user(username_or_email: str, password: str, remember: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Authenticate user and create session.
        Supports login with either username or email.

        Args:
            username_or_email (str): Username or email address
            password (str): Plain text password to verify
            remember (bool): Whether to remember the user session

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
            Returns (True, None) on success, (False, error_message) on failure
        """
        # Normalize input
        username_or_email = username_or_email.strip()

        # Try to find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email.lower())
        ).first()

        # Verify user exists
        if not user:
            return False, 'Invalid username/email or password'

        # Check if account is active
        if not user.is_active:
            return False, 'Account has been deactivated. Please contact support.'

        # Verify password
        if not user.check_password(password):
            return False, 'Invalid username/email or password'

        # Log the user in (creates session)
        login_user(user, remember=remember)

        # Update last login timestamp
        user.update_last_login()

        return True, None

    @staticmethod
    def logout_user() -> bool:
        """
        Log out the current user and clear session.

        Returns:
            bool: True if logout successful
        """
        logout_user()
        return True

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Change user's password.
        Verifies current password before allowing change.

        Args:
            user (User): The user object
            current_password (str): Current password for verification
            new_password (str): New password to set

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Verify current password
        if not user.check_password(current_password):
            return False, 'Current password is incorrect'

        # Check if new password is different
        if user.check_password(new_password):
            return False, 'New password must be different from current password'

        try:
            # Set new password (will be hashed automatically)
            user.password = new_password
            user.updated_at = datetime.now(timezone.utc)

            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f'Failed to change password: {str(e)}'

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Retrieve user by ID.

        Args:
            user_id (int): The user ID

        Returns:
            Optional[User]: User object or None if not found
        """
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Retrieve user by username.

        Args:
            username (str): The username

        Returns:
            Optional[User]: User object or None if not found
        """
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Retrieve user by email.

        Args:
            email (str): The email address

        Returns:
            Optional[User]: User object or None if not found
        """
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def deactivate_user(user: User) -> Tuple[bool, Optional[str]]:
        """
        Deactivate a user account.
        User won't be able to login but data is preserved.

        Args:
            user (User): The user to deactivate

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to deactivate user: {str(e)}'

    @staticmethod
    def activate_user(user: User) -> Tuple[bool, Optional[str]]:
        """
        Activate a user account.

        Args:
            user (User): The user to activate

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f'Failed to activate user: {str(e)}'
