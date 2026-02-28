"""
Model tests.
Tests for database models and relationships.
"""
import pytest
from app.models import User, Post
from datetime import datetime


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            from app.extensions import db
            user = User(
                username='modeltest',
                email='modeltest@example.com',
                is_active=True,
                is_admin=False
            )
            user.password = 'ModelPassword123'

            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.created_at is not None
            assert user.updated_at is not None

    def test_user_password_hashing(self, app):
        """Test that password is hashed."""
        with app.app_context():
            user = User(username='hashtest', email='hash@test.com')
            user.password = 'PlainPassword'

            assert user.password_hash != 'PlainPassword'
            assert len(user.password_hash) > 20

    def test_user_password_verification(self, app):
        """Test password verification."""
        with app.app_context():
            user = User(username='verifytest', email='verify@test.com')
            user.password = 'TestPassword123'

            assert user.check_password('TestPassword123') is True
            assert user.check_password('WrongPassword') is False

    def test_user_password_not_accessible(self, test_user):
        """Test that password property raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = test_user.password

    def test_user_repr(self, test_user):
        """Test user string representation."""
        assert 'testuser' in repr(test_user)

    def test_user_is_active_default(self, app):
        """Test that is_active defaults to True."""
        with app.app_context():
            from app.extensions import db
            user = User(username='activetest', email='active@test.com')
            user.password = 'Password123'
            db.session.add(user)
            db.session.commit()

            assert user.is_active is True

    def test_user_is_admin_default(self, app):
        """Test that is_admin defaults to False."""
        with app.app_context():
            from app.extensions import db
            user = User(username='admintest', email='admintest@test.com')
            user.password = 'Password123'
            db.session.add(user)
            db.session.commit()

            assert user.is_admin is False

    def test_user_update_last_login(self, app, test_user):
        """Test updating last login timestamp."""
        with app.app_context():
            old_last_login = test_user.last_login
            test_user.update_last_login()

            assert test_user.last_login is not None
            if old_last_login:
                assert test_user.last_login > old_last_login


class TestPostModel:
    """Tests for Post model."""

    def test_post_creation(self, app, test_user):
        """Test creating a post."""
        with app.app_context():
            from app.extensions import db
            post = Post(
                title='Model Test Post',
                body='This is a test post for the model.',
                author_id=test_user.id
            )

            db.session.add(post)
            db.session.commit()

            assert post.id is not None
            assert post.created is not None

    def test_post_repr(self, test_post):
        """Test post string representation."""
        assert 'Test Post' in repr(test_post)

    def test_post_author_relationship(self, test_post, test_user):
        """Test post-author relationship."""
        assert test_post.author is not None
        assert test_post.author.id == test_user.id
        assert test_post.author.username == 'testuser'

    def test_user_posts_relationship(self, test_user, test_post):
        """Test user-posts relationship."""
        assert len(test_user.posts) > 0
        assert test_post in test_user.posts

    def test_post_cascade_delete(self, app, test_user):
        """Test that deleting user deletes their posts."""
        with app.app_context():
            from app.extensions import db

            # Create user and post
            user = User(username='cascadetest', email='cascade@test.com')
            user.password = 'Password123'
            db.session.add(user)
            db.session.commit()

            post = Post(
                title='Cascade Test',
                body='This post should be deleted with user.',
                author_id=user.id
            )
            db.session.add(post)
            db.session.commit()

            post_id = post.id
            user_id = user.id

            # Delete user
            db.session.delete(user)
            db.session.commit()

            # Verify post was also deleted
            post = Post.query.get(post_id)
            assert post is None
