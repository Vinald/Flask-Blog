"""
Test configuration and fixtures.
Provides reusable test fixtures for the Flask Blog application.
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Post
from datetime import datetime, timezone


@pytest.fixture(scope='session')
def app():
    """
    Create application instance for testing.
    Uses in-memory SQLite database for fast testing.
    """
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'SECRET_KEY': 'test-secret-key'
    }

    app = create_app(test_config)

    # Create tables
    with app.app_context():
        db.create_all()

    yield app

    # Cleanup
    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create test client for making requests.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create test CLI runner.
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Create database session for each test.
    Rolls back changes after each test.
    """
    with app.app_context():
        # Begin transaction
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind session to connection
        session = db.create_scoped_session(
            options={'bind': connection, 'binds': {}}
        )
        db.session = session

        yield session

        # Rollback transaction
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture(scope='function')
def test_user(app):
    """
    Create a test user in the database.
    """
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            is_active=True,
            is_admin=False
        )
        user.password = 'TestPassword123'
        db.session.add(user)
        db.session.commit()

        # Refresh to get ID
        db.session.refresh(user)
        user_id = user.id

        yield user

        # Cleanup
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(scope='function')
def admin_user(app):
    """
    Create an admin test user.
    """
    with app.app_context():
        user = User(
            username='adminuser',
            email='admin@example.com',
            is_active=True,
            is_admin=True
        )
        user.password = 'AdminPassword123'
        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)

        yield user

        # Cleanup
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(scope='function')
def test_post(app, test_user):
    """
    Create a test blog post.
    """
    with app.app_context():
        post = Post(
            title='Test Post',
            body='This is a test post content.',
            author_id=test_user.id
        )
        db.session.add(post)
        db.session.commit()

        db.session.refresh(post)

        yield post

        # Cleanup
        db.session.delete(post)
        db.session.commit()


@pytest.fixture(scope='function')
def multiple_posts(app, test_user):
    """
    Create multiple test posts.
    """
    with app.app_context():
        posts = []
        for i in range(5):
            post = Post(
                title=f'Test Post {i+1}',
                body=f'This is test post content number {i+1}.',
                author_id=test_user.id
            )
            db.session.add(post)
            posts.append(post)

        db.session.commit()

        for post in posts:
            db.session.refresh(post)

        yield posts

        # Cleanup
        for post in posts:
            db.session.delete(post)
        db.session.commit()


@pytest.fixture(scope='function')
def authenticated_client(client, test_user):
    """
    Create an authenticated test client.
    """
    # Login the test user
    client.post('/api/v1/auth/login', data={
        'username_or_email': 'testuser',
        'password': 'TestPassword123',
        'remember_me': False
    }, follow_redirects=True)

    yield client

    # Logout
    client.get('/api/v1/auth/logout')


@pytest.fixture(scope='function')
def authenticated_admin_client(client, admin_user):
    """
    Create an authenticated admin client.
    """
    # Login the admin user
    client.post('/api/v1/auth/login', data={
        'username_or_email': 'adminuser',
        'password': 'AdminPassword123',
        'remember_me': False
    }, follow_redirects=True)

    yield client

    # Logout
    client.get('/api/v1/auth/logout')
