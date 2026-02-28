"""
API tests.
Tests for RESTful API endpoints with Swagger documentation.
"""
import pytest
import json


class TestAuthAPI:
    """Tests for Authentication API endpoints."""

    def test_auth_status_not_authenticated(self, client):
        """Test auth status when not logged in."""
        response = client.get('/api/v1/auth/status')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is False

    def test_auth_status_authenticated(self, authenticated_client):
        """Test auth status when logged in."""
        response = authenticated_client.get('/api/v1/auth/status')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is True
        assert data['user']['username'] == 'testuser'

    def test_register_api(self, client, app):
        """Test user registration via API."""
        response = client.post('/api/v1/auth/register',
            json={
                'username': 'apiuser',
                'email': 'api@example.com',
                'password': 'ApiPassword123'
            },
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'
        assert data['data']['username'] == 'apiuser'

    def test_register_api_duplicate_username(self, client, test_user):
        """Test API registration with duplicate username."""
        response = client.post('/api/v1/auth/register',
            json={
                'username': 'testuser',
                'email': 'new@example.com',
                'password': 'Password123'
            },
            content_type='application/json'
        )

        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['errors']['detail']

    def test_login_api(self, client, test_user):
        """Test user login via API."""
        response = client.post('/api/v1/auth/login',
            json={
                'username_or_email': 'testuser',
                'password': 'TestPassword123',
                'remember_me': False
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['data']['username'] == 'testuser'

    def test_login_api_wrong_password(self, client, test_user):
        """Test API login with wrong password."""
        response = client.post('/api/v1/auth/login',
            json={
                'username_or_email': 'testuser',
                'password': 'WrongPassword',
                'remember_me': False
            },
            content_type='application/json'
        )

        assert response.status_code == 401

    def test_profile_api_requires_auth(self, client):
        """Test that profile API requires authentication."""
        response = client.get('/api/v1/auth/profile')

        assert response.status_code == 401 or response.status_code == 302

    def test_profile_api(self, authenticated_client):
        """Test getting profile via API."""
        response = authenticated_client.get('/api/v1/auth/profile')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'

    def test_logout_api(self, authenticated_client):
        """Test logout via API."""
        response = authenticated_client.post('/api/v1/auth/logout')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Logged out' in data['message']


class TestBlogPostsAPI:
    """Tests for Blog Posts API endpoints."""

    def test_list_posts_api(self, client, test_post):
        """Test listing posts via API."""
        response = client.get('/api/v1/posts/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'posts' in data
        assert 'pagination' in data
        assert len(data['posts']) > 0

    def test_list_posts_pagination(self, client, multiple_posts):
        """Test API pagination."""
        response = client.get('/api/v1/posts/?page=1&per_page=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['posts']) <= 2
        assert data['pagination']['per_page'] == 2

    def test_get_post_api(self, client, test_post):
        """Test getting single post via API."""
        response = client.get(f'/api/v1/posts/{test_post.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Test Post'
        assert data['author']['username'] == 'testuser'

    def test_get_nonexistent_post_api(self, client):
        """Test getting non-existent post via API."""
        response = client.get('/api/v1/posts/99999')

        assert response.status_code == 404

    def test_create_post_api_requires_auth(self, client):
        """Test that creating post via API requires auth."""
        response = client.post('/api/v1/posts/',
            json={
                'title': 'API Post',
                'body': 'Created via API'
            },
            content_type='application/json'
        )

        assert response.status_code == 401 or response.status_code == 302

    def test_create_post_api(self, authenticated_client):
        """Test creating post via API."""
        response = authenticated_client.post('/api/v1/posts/',
            json={
                'title': 'API Test Post',
                'body': 'This post was created via API.'
            },
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'API Test Post'
        assert data['author']['username'] == 'testuser'

    def test_update_post_api(self, authenticated_client, test_post):
        """Test updating post via API."""
        response = authenticated_client.put(f'/api/v1/posts/{test_post.id}',
            json={
                'title': 'Updated via API',
                'body': 'Updated content'
            },
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated via API'

    def test_update_post_api_requires_permission(self, client, test_post, app):
        """Test that updating post requires permission."""
        # Create and login as different user
        with app.app_context():
            from app.models import User
            from app.extensions import db
            other_user = User(username='apiother', email='apiother@example.com')
            other_user.password = 'OtherPassword123'
            db.session.add(other_user)
            db.session.commit()

        # Login as other user
        client.post('/api/v1/auth/login',
            json={
                'username_or_email': 'apiother',
                'password': 'OtherPassword123'
            },
            content_type='application/json'
        )

        # Try to update test_post
        response = client.put(f'/api/v1/posts/{test_post.id}',
            json={'title': 'Hacked'},
            content_type='application/json'
        )

        assert response.status_code == 403

    def test_delete_post_api(self, authenticated_client, test_post):
        """Test deleting post via API."""
        post_id = test_post.id
        response = authenticated_client.delete(f'/api/v1/posts/{post_id}')

        assert response.status_code == 200

        # Verify post is deleted
        response = authenticated_client.get(f'/api/v1/posts/{post_id}')
        assert response.status_code == 404

    def test_search_posts_api(self, client, test_post):
        """Test searching posts via API."""
        response = client.get('/api/v1/posts/search?q=Test')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['posts']) > 0
        assert data['query'] == 'Test'

    def test_search_posts_api_no_query(self, client):
        """Test search API without query."""
        response = client.get('/api/v1/posts/search')

        assert response.status_code == 400

    def test_author_posts_api(self, client, test_user, test_post):
        """Test getting author's posts via API."""
        response = client.get(f'/api/v1/posts/author/{test_user.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['author']['username'] == 'testuser'
        assert len(data['posts']) > 0

    def test_my_posts_api(self, authenticated_client, test_post):
        """Test getting own posts via API."""
        response = authenticated_client.get('/api/v1/posts/my-posts')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['posts']) > 0


class TestUsersAPI:
    """Tests for Users API endpoints."""

    def test_list_users_api(self, client, test_user):
        """Test listing users via API."""
        response = client.get('/api/v1/users/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'total' in data
        assert data['total'] > 0

    def test_get_user_by_id_api(self, client, test_user):
        """Test getting user by ID via API."""
        response = client.get(f'/api/v1/users/{test_user.id}')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'

    def test_get_user_by_username_api(self, client, test_user):
        """Test getting user by username via API."""
        response = client.get('/api/v1/users/testuser')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'testuser'

    def test_get_nonexistent_user_api(self, client):
        """Test getting non-existent user via API."""
        response = client.get('/api/v1/users/99999')

        assert response.status_code == 404

    def test_user_stats_api(self, client, test_user, test_post):
        """Test getting user statistics via API."""
        response = client.get('/api/v1/users/stats')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_users' in data
        assert 'total_posts' in data
        assert data['total_users'] > 0


class TestSwaggerUI:
    """Tests for Swagger UI documentation."""

    def test_swagger_ui_loads(self, client):
        """Test that Swagger UI page loads."""
        response = client.get('/api/v1/docs')

        assert response.status_code == 200
        assert b'swagger' in response.data.lower()

    def test_swagger_json_loads(self, client):
        """Test that Swagger JSON spec loads."""
        response = client.get('/api/v1/swagger.json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'swagger' in data or 'openapi' in data
        assert 'paths' in data
