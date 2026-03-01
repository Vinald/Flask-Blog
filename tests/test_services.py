"""
Service layer tests.
Tests for AuthService and BlogService business logic.
"""
import pytest
from app.services.auth_service import AuthService
from app.services.blog_service import BlogService
from app.models import User, Post


class TestAuthService:
    """Tests for AuthService class."""

    def test_register_user_success(self, app):
        """Test successful user registration."""
        with app.app_context():
            user, error = AuthService.register_user(
                username='servicetest',
                email='service@example.com',
                password='ServicePass123'
            )

            assert error is None
            assert user is not None
            assert user.username == 'servicetest'
            assert user.email == 'service@example.com'

    def test_register_user_duplicate_username(self, app, test_user):
        """Test registration with duplicate username."""
        with app.app_context():
            user, error = AuthService.register_user(
                username='testuser',
                email='new@example.com',
                password='Password123'
            )

            assert user is None
            assert 'already exists' in error

    def test_authenticate_user_success(self, app, test_user):
        """Test successful authentication."""
        with app.app_context():
            success, error = AuthService.authenticate_user(
                username_or_email='testuser',
                password='TestPassword123',
                remember=False
            )

            assert success is True
            assert error is None

    def test_authenticate_user_wrong_password(self, app, test_user):
        """Test authentication with wrong password."""
        with app.app_context():
            success, error = AuthService.authenticate_user(
                username_or_email='testuser',
                password='WrongPassword',
                remember=False
            )

            assert success is False
            assert error is not None

    def test_authenticate_user_with_email(self, app, test_user):
        """Test authentication using email."""
        with app.app_context():
            success, error = AuthService.authenticate_user(
                username_or_email='test@example.com',
                password='TestPassword123',
                remember=False
            )

            assert success is True
            assert error is None

    def test_get_user_by_username(self, app, test_user):
        """Test getting user by username."""
        with app.app_context():
            user = AuthService.get_user_by_username('testuser')

            assert user is not None
            assert user.username == 'testuser'

    def test_get_user_by_email(self, app, test_user):
        """Test getting user by email."""
        with app.app_context():
            user = AuthService.get_user_by_email('test@example.com')

            assert user is not None
            assert user.email == 'test@example.com'

    def test_deactivate_user(self, app, test_user):
        """Test user deactivation."""
        with app.app_context():
            success, error = AuthService.deactivate_user(test_user)

            assert success is True
            assert error is None
            assert test_user.is_active is False


class TestBlogService:
    """Tests for BlogService class."""

    def test_create_post_success(self, app, test_user):
        """Test successful post creation."""
        with app.app_context():
            post, error = BlogService.create_post(
                author_id=test_user.id,
                title='Service Test Post',
                body='This is a service test post content.'
            )

            assert error is None
            assert post is not None
            assert post.title == 'Service Test Post'
            assert post.author_id == test_user.id

    def test_create_post_short_title(self, app, test_user):
        """Test creating post with too short title."""
        with app.app_context():
            post, error = BlogService.create_post(
                author_id=test_user.id,
                title='Hi',
                body='Valid content here.'
            )

            assert post is None
            assert 'at least 3 characters' in error

    def test_create_post_short_body(self, app, test_user):
        """Test creating post with too short body."""
        with app.app_context():
            post, error = BlogService.create_post(
                author_id=test_user.id,
                title='Valid Title',
                body='Short'
            )

            assert post is None
            assert 'at least 10 characters' in error

    def test_get_post_by_id(self, app, test_post):
        """Test getting post by ID."""
        with app.app_context():
            post = BlogService.get_post_by_id(test_post.id)

            assert post is not None
            assert post.id == test_post.id

    def test_get_all_posts(self, app, multiple_posts):
        """Test getting all posts."""
        with app.app_context():
            result = BlogService.get_all_posts(page=1, per_page=10)

            assert 'posts' in result
            assert result['total'] == 5
            assert len(result['posts']) == 5

    def test_get_posts_by_author(self, app, test_user, multiple_posts):
        """Test getting posts by author."""
        with app.app_context():
            result = BlogService.get_posts_by_author(
                author_id=test_user.id,
                page=1,
                per_page=10
            )

            assert 'posts' in result
            assert result['total'] == 5

    def test_update_post_success(self, app, test_post):
        """Test successful post update."""
        with app.app_context():
            success, error = BlogService.update_post(
                post=test_post,
                title='Updated Title',
                body='Updated body content'
            )

            assert success is True
            assert error is None
            assert test_post.title == 'Updated Title'

    def test_delete_post_success(self, app, test_post):
        """Test successful post deletion."""
        with app.app_context():
            post_id = test_post.id
            # Get fresh instance from current session
            post = Post.query.get(post_id)

            success, error = BlogService.delete_post(post)

            assert success is True
            assert error is None

            # Verify deletion
            deleted_post = Post.query.get(post_id)
            assert deleted_post is None

    def test_can_edit_post_author(self, app, test_user, test_post):
        """Test that author can edit own post."""
        with app.app_context():
            can_edit = BlogService.can_edit_post(test_user.id, test_post)

            assert can_edit is True

    def test_can_edit_post_admin(self, app, admin_user, test_post):
        """Test that admin can edit any post."""
        with app.app_context():
            can_edit = BlogService.can_edit_post(admin_user.id, test_post)

            assert can_edit is True

    def test_can_edit_post_other_user(self, app, test_post):
        """Test that other users cannot edit post."""
        with app.app_context():
            # Create another user
            from app.extensions import db
            other_user = User(username='otherserviceuser', email='otherservice@example.com')
            other_user.password = 'Password123'
            db.session.add(other_user)
            db.session.commit()

            can_edit = BlogService.can_edit_post(other_user.id, test_post)

            assert can_edit is False

    def test_search_posts(self, app, test_post):
        """Test post search functionality."""
        with app.app_context():
            result = BlogService.search_posts(query='Test', page=1, per_page=10)

            assert 'posts' in result
            assert len(result['posts']) > 0
            assert result['query'] == 'Test'
