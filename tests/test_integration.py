"""
Integration tests.
Tests for complete workflows and integration between components.
"""
import pytest
import json


class TestCompleteAuthFlow:
    """Test complete authentication workflow."""

    def test_register_login_logout_flow(self, client):
        """Test complete user journey: register -> login -> logout."""
        # Register
        response = client.post('/auth/register', data={
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password': 'FlowPassword123',
            'confirm_password': 'FlowPassword123'
        }, follow_redirects=True)

        assert b'Account created successfully' in response.data

        # Login
        response = client.post('/auth/login', data={
            'username_or_email': 'flowuser',
            'password': 'FlowPassword123'
        }, follow_redirects=True)

        assert b'Welcome back' in response.data

        # Access profile
        response = client.get('/auth/profile')
        assert response.status_code == 200
        assert b'flowuser' in response.data

        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert b'logged out' in response.data


class TestCompleteBlogFlow:
    """Test complete blog workflow."""

    def test_create_view_edit_delete_post_flow(self, authenticated_client, app):
        """Test complete post lifecycle: create -> view -> edit -> delete."""
        # Create post
        response = authenticated_client.post('/blog/create', data={
            'title': 'Flow Test Post',
            'body': 'This is a complete flow test post.'
        }, follow_redirects=True)

        assert b'created successfully' in response.data

        # Get the post ID from database
        with app.app_context():
            from app.models import Post
            post = Post.query.filter_by(title='Flow Test Post').first()
            post_id = post.id

        # View post
        response = authenticated_client.get(f'/blog/post/{post_id}')
        assert response.status_code == 200
        assert b'Flow Test Post' in response.data

        # Edit post
        response = authenticated_client.post(f'/blog/post/{post_id}/edit', data={
            'title': 'Updated Flow Post',
            'body': 'This content has been updated.'
        }, follow_redirects=True)

        assert b'updated successfully' in response.data

        # Delete post
        response = authenticated_client.post(f'/blog/post/{post_id}/delete', follow_redirects=True)
        assert b'deleted successfully' in response.data

        # Verify deletion
        response = authenticated_client.get(f'/blog/post/{post_id}', follow_redirects=True)
        assert b'not found' in response.data.lower() or response.status_code == 404


class TestAPIIntegration:
    """Test API integration with web interface."""

    def test_api_and_web_share_session(self, client, test_user):
        """Test that API and web interface share authentication."""
        # Login via web interface
        client.post('/auth/login', data={
            'username_or_email': 'testuser',
            'password': 'TestPassword123'
        }, follow_redirects=True)

        # Check auth status via API
        response = client.get('/api/v1/auth/status')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is True

    def test_create_post_web_view_api(self, authenticated_client, app):
        """Test creating post via web and viewing via API."""
        # Create via web
        authenticated_client.post('/blog/create', data={
            'title': 'Web Created Post',
            'body': 'This post was created via web interface.'
        }, follow_redirects=True)

        # Get via API
        response = authenticated_client.get('/api/v1/posts/')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Find the post
        post_found = any(post['title'] == 'Web Created Post' for post in data['posts'])
        assert post_found is True

    def test_create_post_api_view_web(self, authenticated_client):
        """Test creating post via API and viewing via web."""
        # Create via API
        response = authenticated_client.post('/api/v1/posts/',
            json={
                'title': 'API Created Post',
                'body': 'This post was created via API.'
            },
            content_type='application/json'
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        post_id = data['id']

        # View via web
        response = authenticated_client.get(f'/blog/post/{post_id}')

        assert response.status_code == 200
        assert b'API Created Post' in response.data


class TestPermissions:
    """Test permission and authorization."""

    def test_admin_can_edit_any_post(self, authenticated_admin_client, test_post):
        """Test that admin can edit any user's post."""
        response = authenticated_admin_client.get(f'/blog/post/{test_post.id}/edit')

        assert response.status_code == 200
        assert b'Edit Post' in response.data

    def test_admin_can_delete_any_post(self, authenticated_admin_client, test_post):
        """Test that admin can delete any user's post."""
        response = authenticated_admin_client.post(
            f'/blog/post/{test_post.id}/delete',
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'deleted successfully' in response.data


class TestSearchFunctionality:
    """Test search across different interfaces."""

    def test_search_web(self, client, test_post):
        """Test search via web interface."""
        response = client.get('/blog/search?q=Test')

        assert response.status_code == 200
        assert b'Test Post' in response.data

    def test_search_api(self, client, test_post):
        """Test search via API."""
        response = client.get('/api/v1/posts/search?q=Test')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['posts']) > 0
        assert data['posts'][0]['title'] == 'Test Post'


class TestPagination:
    """Test pagination across different interfaces."""

    def test_web_pagination(self, client, multiple_posts):
        """Test pagination on web interface."""
        response = client.get('/blog/?page=1')

        assert response.status_code == 200
        assert b'Test Post' in response.data

    def test_api_pagination(self, client, multiple_posts):
        """Test pagination via API."""
        response = client.get('/api/v1/posts/?page=1&per_page=2')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['posts']) == 2
        assert data['pagination']['total'] == 5
