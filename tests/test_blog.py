"""
Blog post tests.
Tests for blog post CRUD operations and related functionality.
"""
import pytest
from app.models import Post


class TestBlogIndex:
    """Tests for blog index/listing page."""

    def test_blog_index_loads(self, client):
        """Test that blog index page loads."""
        response = client.get('/blog/')
        assert response.status_code == 200

    def test_blog_index_shows_posts(self, client, test_post):
        """Test that blog index displays posts."""
        response = client.get('/blog/')

        assert response.status_code == 200
        assert b'Test Post' in response.data

    def test_blog_index_pagination(self, client, multiple_posts):
        """Test that pagination works on blog index."""
        response = client.get('/blog/?page=1')

        assert response.status_code == 200
        # Should show posts
        assert b'Test Post' in response.data

    def test_blog_index_empty(self, client):
        """Test blog index with no posts."""
        response = client.get('/blog/')

        assert response.status_code == 200
        assert b'No posts yet' in response.data


class TestPostCreation:
    """Tests for creating blog posts."""

    def test_create_post_requires_login(self, client):
        """Test that creating post requires authentication."""
        response = client.get('/blog/create', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_create_post_page_loads(self, authenticated_client):
        """Test that create post page loads."""
        response = authenticated_client.get('/blog/create')

        assert response.status_code == 200
        assert b'Create New Post' in response.data

    def test_create_post_success(self, authenticated_client, app):
        """Test successful post creation."""
        response = authenticated_client.post('/blog/create', data={
            'title': 'New Test Post',
            'body': 'This is the content of my new test post.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'created successfully' in response.data

        # Verify post was created
        with app.app_context():
            post = Post.query.filter_by(title='New Test Post').first()
            assert post is not None
            assert post.body == 'This is the content of my new test post.'

    def test_create_post_short_title(self, authenticated_client):
        """Test creating post with too short title."""
        response = authenticated_client.post('/blog/create', data={
            'title': 'Hi',
            'body': 'This is the content.'
        })

        assert response.status_code == 200
        assert b'at least 3 characters' in response.data

    def test_create_post_short_body(self, authenticated_client):
        """Test creating post with too short body."""
        response = authenticated_client.post('/blog/create', data={
            'title': 'Valid Title',
            'body': 'Short'
        })

        assert response.status_code == 200
        assert b'at least 10 characters' in response.data


class TestPostViewing:
    """Tests for viewing blog posts."""

    def test_view_post(self, client, test_post):
        """Test viewing a single post."""
        response = client.get(f'/blog/post/{test_post.id}')

        assert response.status_code == 200
        assert b'Test Post' in response.data
        assert b'test post content' in response.data

    def test_view_nonexistent_post(self, client):
        """Test viewing non-existent post."""
        response = client.get('/blog/post/99999', follow_redirects=True)

        # Should redirect or show error
        assert response.status_code == 200

    def test_view_post_shows_author(self, client, test_post):
        """Test that post view shows author information."""
        response = client.get(f'/blog/post/{test_post.id}')

        assert response.status_code == 200
        assert b'testuser' in response.data


class TestPostEditing:
    """Tests for editing blog posts."""

    def test_edit_post_requires_login(self, client, test_post):
        """Test that editing requires authentication."""
        response = client.get(f'/blog/post/{test_post.id}/edit', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_edit_own_post_page_loads(self, authenticated_client, test_post):
        """Test that edit page loads for post owner."""
        response = authenticated_client.get(f'/blog/post/{test_post.id}/edit')

        assert response.status_code == 200
        assert b'Edit Post' in response.data
        assert b'Test Post' in response.data

    def test_edit_post_success(self, authenticated_client, test_post):
        """Test successful post editing."""
        response = authenticated_client.post(f'/blog/post/{test_post.id}/edit', data={
            'title': 'Updated Test Post',
            'body': 'This is the updated content.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'updated successfully' in response.data
        assert b'Updated Test Post' in response.data

    def test_edit_other_user_post_forbidden(self, client, test_post, app):
        """Test that user cannot edit another user's post."""
        # Create and login as different user
        with app.app_context():
            from app.models import User
            other_user = User(username='otheruser', email='other@example.com')
            other_user.password = 'OtherPassword123'
            from app.extensions import db
            db.session.add(other_user)
            db.session.commit()

        # Login as other user
        client.post('/auth/login', data={
            'username_or_email': 'otheruser',
            'password': 'OtherPassword123'
        }, follow_redirects=True)

        # Try to edit test_post (owned by testuser)
        response = client.get(f'/blog/post/{test_post.id}/edit', follow_redirects=True)

        assert b'do not have permission' in response.data

    def test_admin_can_edit_any_post(self, authenticated_admin_client, test_post):
        """Test that admin can edit any post."""
        response = authenticated_admin_client.get(f'/blog/post/{test_post.id}/edit')

        assert response.status_code == 200
        assert b'Edit Post' in response.data


class TestPostDeletion:
    """Tests for deleting blog posts."""

    def test_delete_post_requires_login(self, client, test_post):
        """Test that deleting requires authentication."""
        response = client.post(f'/blog/post/{test_post.id}/delete', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_delete_own_post(self, authenticated_client, test_post, app):
        """Test deleting own post."""
        post_id = test_post.id

        response = authenticated_client.post(f'/blog/post/{post_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert b'deleted successfully' in response.data

        # Verify post was deleted
        with app.app_context():
            post = Post.query.get(post_id)
            assert post is None

    def test_delete_other_user_post_forbidden(self, client, test_post, app):
        """Test that user cannot delete another user's post."""
        # Create and login as different user
        with app.app_context():
            from app.models import User
            other_user = User(username='otheruser2', email='other2@example.com')
            other_user.password = 'OtherPassword123'
            from app.extensions import db
            db.session.add(other_user)
            db.session.commit()

        # Login as other user
        client.post('/auth/login', data={
            'username_or_email': 'otheruser2',
            'password': 'OtherPassword123'
        }, follow_redirects=True)

        # Try to delete test_post
        response = client.post(f'/blog/post/{test_post.id}/delete', follow_redirects=True)

        assert b'do not have permission' in response.data

    def test_admin_can_delete_any_post(self, authenticated_admin_client, test_post, app):
        """Test that admin can delete any post."""
        post_id = test_post.id

        response = authenticated_admin_client.post(f'/blog/post/{post_id}/delete', follow_redirects=True)

        assert response.status_code == 200
        assert b'deleted successfully' in response.data


class TestMyPosts:
    """Tests for 'My Posts' page."""

    def test_my_posts_requires_login(self, client):
        """Test that My Posts requires authentication."""
        response = client.get('/blog/my-posts', follow_redirects=True)

        assert b'log in' in response.data.lower()

    def test_my_posts_page_loads(self, authenticated_client):
        """Test that My Posts page loads."""
        response = authenticated_client.get('/blog/my-posts')

        assert response.status_code == 200
        assert b'My Posts' in response.data

    def test_my_posts_shows_user_posts(self, authenticated_client, test_post):
        """Test that My Posts shows user's posts."""
        response = authenticated_client.get('/blog/my-posts')

        assert response.status_code == 200
        assert b'Test Post' in response.data

    def test_my_posts_empty(self, authenticated_client):
        """Test My Posts with no posts."""
        response = authenticated_client.get('/blog/my-posts')

        assert response.status_code == 200
        assert b'haven\'t created any posts' in response.data or b'No posts' in response.data


class TestAuthorPosts:
    """Tests for author posts page."""

    def test_author_posts_page_loads(self, client, test_user, test_post):
        """Test that author posts page loads."""
        response = client.get(f'/blog/author/{test_user.id}')

        assert response.status_code == 200
        assert b'testuser' in response.data
        assert b'Test Post' in response.data

    def test_author_posts_nonexistent_user(self, client):
        """Test author posts for non-existent user."""
        response = client.get('/blog/author/99999', follow_redirects=True)

        # Should redirect or show error
        assert response.status_code == 200


class TestPostSearch:
    """Tests for post search functionality."""

    def test_search_page_loads(self, client):
        """Test that search works."""
        response = client.get('/blog/search?q=test')

        assert response.status_code == 200

    def test_search_finds_posts(self, client, test_post):
        """Test that search finds matching posts."""
        response = client.get('/blog/search?q=Test')

        assert response.status_code == 200
        assert b'Test Post' in response.data

    def test_search_no_results(self, client):
        """Test search with no results."""
        response = client.get('/blog/search?q=nonexistent')

        assert response.status_code == 200
        assert b'No results' in response.data or b'0 result' in response.data

    def test_search_empty_query(self, client):
        """Test search with empty query."""
        response = client.get('/blog/search?q=', follow_redirects=True)

        assert response.status_code == 200


class TestPostModel:
    """Tests for Post model."""

    def test_post_creation(self, app, test_user):
        """Test creating a post."""
        with app.app_context():
            post = Post(
                title='Model Test Post',
                body='This is a model test.',
                author_id=test_user.id
            )
            from app.extensions import db
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
        assert test_post.author.username == 'testuser'
