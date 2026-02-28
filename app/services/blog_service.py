"""
Blog service layer.
Contains all business logic for blog post management (CRUD operations).
Separates business logic from routes for better maintainability and testing.
"""
from app.models import Post, User
from app.extensions import db
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy import desc


class BlogService:
    """
    Service class for handling blog post operations.
    Provides methods for creating, reading, updating, and deleting posts.
    """

    @staticmethod
    def create_post(author_id: int, title: str, body: str) -> Tuple[Optional[Post], Optional[str]]:
        """
        Create a new blog post.

        Args:
            author_id (int): ID of the user creating the post
            title (str): Post title
            body (str): Post content

        Returns:
            Tuple[Optional[Post], Optional[str]]: (Post object, error message)
            Returns (Post, None) on success, (None, error_message) on failure
        """
        # Validate inputs
        if not title or len(title.strip()) < 3:
            return None, 'Title must be at least 3 characters'

        if not body or len(body.strip()) < 10:
            return None, 'Content must be at least 10 characters'

        # Check if author exists
        author = User.query.get(author_id)
        if not author:
            return None, 'Author not found'

        try:
            # Create new post
            post = Post(
                author_id=author_id,
                title=title.strip(),
                body=body.strip()
            )

            db.session.add(post)
            db.session.commit()

            return post, None

        except Exception as e:
            db.session.rollback()
            return None, f'Failed to create post: {str(e)}'

    @staticmethod
    def get_post_by_id(post_id: int) -> Optional[Post]:
        """
        Retrieve a single post by ID.

        Args:
            post_id (int): The post ID

        Returns:
            Optional[Post]: Post object or None if not found
        """
        return Post.query.get(post_id)

    @staticmethod
    def get_all_posts(page: int = 1, per_page: int = 10) -> dict:
        """
        Retrieve all posts with pagination, ordered by most recent first.

        Args:
            page (int): Page number (1-indexed)
            per_page (int): Number of posts per page

        Returns:
            dict: Contains 'posts', 'total', 'pages', 'current_page', 'has_prev', 'has_next'
        """
        # Query posts ordered by creation date (newest first)
        pagination = Post.query.order_by(desc(Post.created)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'posts': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }

    @staticmethod
    def get_posts_by_author(author_id: int, page: int = 1, per_page: int = 10) -> dict:
        """
        Retrieve all posts by a specific author with pagination.

        Args:
            author_id (int): The author's user ID
            page (int): Page number (1-indexed)
            per_page (int): Number of posts per page

        Returns:
            dict: Contains 'posts', 'total', 'pages', etc.
        """
        pagination = Post.query.filter_by(author_id=author_id).order_by(
            desc(Post.created)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'posts': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num
        }

    @staticmethod
    def update_post(post: Post, title: str = None, body: str = None) -> Tuple[bool, Optional[str]]:
        """
        Update an existing blog post.

        Args:
            post (Post): The post object to update
            title (str, optional): New title (if provided)
            body (str, optional): New body content (if provided)

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Validate inputs if provided
        if title is not None:
            if len(title.strip()) < 3:
                return False, 'Title must be at least 3 characters'
            post.title = title.strip()

        if body is not None:
            if len(body.strip()) < 10:
                return False, 'Content must be at least 10 characters'
            post.body = body.strip()

        try:
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f'Failed to update post: {str(e)}'

    @staticmethod
    def delete_post(post: Post) -> Tuple[bool, Optional[str]]:
        """
        Delete a blog post.

        Args:
            post (Post): The post to delete

        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        try:
            db.session.delete(post)
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, f'Failed to delete post: {str(e)}'

    @staticmethod
    def can_edit_post(user_id: int, post: Post) -> bool:
        """
        Check if a user can edit a specific post.
        User can edit if they are the author or an admin.

        Args:
            user_id (int): The user's ID
            post (Post): The post to check

        Returns:
            bool: True if user can edit, False otherwise
        """
        user = User.query.get(user_id)
        if not user:
            return False

        # User can edit if they are the author or an admin
        return post.author_id == user_id or user.is_admin

    @staticmethod
    def search_posts(query: str, page: int = 1, per_page: int = 10) -> dict:
        """
        Search posts by title or content.

        Args:
            query (str): Search query string
            page (int): Page number
            per_page (int): Posts per page

        Returns:
            dict: Pagination results
        """
        search_term = f'%{query}%'
        pagination = Post.query.filter(
            (Post.title.ilike(search_term)) | (Post.body.ilike(search_term))
        ).order_by(desc(Post.created)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        return {
            'posts': pagination.items,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'query': query
        }
