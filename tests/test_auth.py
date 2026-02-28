"""
Authentication tests.
Tests for user registration, login, logout, and profile management.
"""
import pytest
from app.models import User


class TestUserRegistration:
    """Tests for user registration functionality."""

    def test_register_page_loads(self, client):
        """Test that registration page loads successfully."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data

    def test_register_new_user(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'confirm_password': 'NewPassword123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Account created successfully' in response.data

        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.is_active is True

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with existing username."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        })

        assert response.status_code == 200
        assert b'Username already exists' in response.data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email."""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists
            'password': 'Password123',
            'confirm_password': 'Password123'
        })

        assert response.status_code == 200
        assert b'Email already registered' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password123',
            'confirm_password': 'DifferentPassword123'
        })

        assert response.status_code == 200
        assert b'Passwords must match' in response.data

    def test_register_short_password(self, client):
        """Test registration with password too short."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'short',
            'confirm_password': 'short'
        })

        assert response.status_code == 200
        assert b'at least 8 characters' in response.data


class TestUserLogin:
    """Tests for user login functionality."""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_with_username(self, client, test_user):
        """Test successful login with username."""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPassword123',
            'remember_me': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Welcome back' in response.data

    def test_login_with_email(self, client, test_user):
        """Test successful login with email."""
        response = client.post('/auth/login', data={
            'username_or_email': 'test@example.com',
            'password': 'TestPassword123',
            'remember_me': False
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Welcome back' in response.data

    def test_login_wrong_password(self, client, test_user):
        """Test login with incorrect password."""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'WrongPassword',
            'remember_me': False
        })

        assert response.status_code == 200
        assert b'Invalid username/email or password' in response.data

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/auth/login', data={
            'username_or_email': 'nonexistent',
            'password': 'Password123',
            'remember_me': False
        })

        assert response.status_code == 200
        assert b'Invalid username/email or password' in response.data

    def test_login_remember_me(self, client, test_user):
        """Test login with remember me option."""
        response = client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPassword123',
            'remember_me': True
        }, follow_redirects=True)

        assert response.status_code == 200
        # Check for remember me cookie
        assert 'remember_token' in [cookie.name for cookie in client.cookie_jar]


class TestUserLogout:
    """Tests for user logout functionality."""

    def test_logout(self, authenticated_client):
        """Test successful logout."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)

        assert response.status_code == 200
        assert b'logged out' in response.data

    def test_logout_requires_login(self, client):
        """Test that logout requires authentication."""
        response = client.get('/auth/logout', follow_redirects=True)

        # Should redirect to login
        assert b'log in' in response.data.lower()


class TestUserProfile:
    """Tests for user profile functionality."""

    def test_profile_requires_login(self, client):
        """Test that profile page requires authentication."""
        response = client.get('/auth/profile', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_profile_page_loads(self, authenticated_client):
        """Test that profile page loads for authenticated user."""
        response = authenticated_client.get('/auth/profile')

        assert response.status_code == 200
        assert b'testuser' in response.data
        assert b'test@example.com' in response.data

    def test_profile_shows_post_count(self, authenticated_client, test_post):
        """Test that profile shows correct post count."""
        response = authenticated_client.get('/auth/profile')

        assert response.status_code == 200
        assert b'Total Posts' in response.data


class TestPasswordChange:
    """Tests for password change functionality."""

    def test_change_password_page_requires_login(self, client):
        """Test that change password page requires authentication."""
        response = client.get('/auth/change-password', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_change_password_page_loads(self, authenticated_client):
        """Test that change password page loads."""
        response = authenticated_client.get('/auth/change-password')

        assert response.status_code == 200
        assert b'Change Password' in response.data

    def test_change_password_success(self, authenticated_client, app):
        """Test successful password change."""
        response = authenticated_client.post('/auth/change-password', data={
            'current_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'confirm_new_password': 'NewPassword456'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Password changed successfully' in response.data

        # Verify new password works
        authenticated_client.get('/auth/logout')
        response = authenticated_client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'NewPassword456',
            'remember_me': False
        }, follow_redirects=True)

        assert b'Welcome back' in response.data

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        response = authenticated_client.post('/auth/change-password', data={
            'current_password': 'WrongPassword',
            'new_password': 'NewPassword456',
            'confirm_new_password': 'NewPassword456'
        })

        assert response.status_code == 200
        assert b'Current password is incorrect' in response.data

    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with mismatched new passwords."""
        response = authenticated_client.post('/auth/change-password', data={
            'current_password': 'TestPassword123',
            'new_password': 'NewPassword456',
            'confirm_new_password': 'DifferentPassword'
        })

        assert response.status_code == 200
        assert b'must match' in response.data


class TestUserModel:
    """Tests for User model methods."""

    def test_password_hashing(self, app):
        """Test that password is hashed."""
        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.password = 'PlainPassword123'

            assert user.password_hash is not None
            assert user.password_hash != 'PlainPassword123'

    def test_password_verification(self, app):
        """Test password verification."""
        with app.app_context():
            user = User(username='verifytest', email='verify@test.com')
            user.password = 'TestPassword123'

            assert user.check_password('TestPassword123') is True
            assert user.check_password('WrongPassword') is False

    def test_password_not_readable(self, test_user):
        """Test that password property is not readable."""
        with pytest.raises(AttributeError):
            _ = test_user.password
