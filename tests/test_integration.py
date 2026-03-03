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



class TestPagination:
    """Test pagination across different interfaces."""

    def test_web_pagination(self, client, multiple_posts):
        """Test pagination on web interface."""
        response = client.get('/blog/?page=1')

        assert response.status_code == 200
        assert b'Test Post' in response.data
