"""
Blog blueprint - handles all blog post routes.
Includes creating, reading, updating, and deleting posts.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.forms.blog import PostForm
from app.services.blog_service import BlogService
from app.models import Post

# Create blog blueprint
# url_prefix='/blog' means all routes will be prefixed with /blog
blog_bp = Blueprint('blog', __name__, url_prefix='/blog')


@blog_bp.route('/')
@blog_bp.route('/posts')
def index():
    """
    Blog home page - displays all posts with pagination.
    Accessible to everyone (no login required).
    """
    # Get page number from query string, default to 1
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get posts from service layer
    result = BlogService.get_all_posts(page=page, per_page=per_page)

    return render_template(
        'blog/index.html',
        title='Blog Posts',
        posts=result['posts'],
        pagination=result
    )


@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    """
    View a single blog post.
    Shows post details and author information.
    Accessible to everyone.

    Args:
        post_id (int): The ID of the post to view
    """
    # Get post or return 404 if not found
    post = BlogService.get_post_by_id(post_id)
    if not post:
        abort(404)

    return render_template(
        'blog/view_post.html',
        title=post.title,
        post=post
    )


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create a new blog post.
    GET: Display post creation form
    POST: Process form and create new post

    Requires user to be logged in.
    """
    form = PostForm()

    # Process form submission
    if form.validate_on_submit():
        # Extract form data
        title = form.title.data
        body = form.body.data

        # Call service layer to create post
        post, error = BlogService.create_post(
            author_id=current_user.id,
            title=title,
            body=body
        )

        if post:
            # Post created successfully
            flash(f'Post "{post.title}" created successfully!', 'success')
            return redirect(url_for('blog.view_post', post_id=post.id))
        else:
            # Post creation failed
            flash(f'Failed to create post: {error}', 'danger')

    # Display form (GET request or validation failed)
    return render_template(
        'blog/create_post.html',
        title='Create Post',
        form=form
    )


@blog_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    Edit an existing blog post.
    GET: Display edit form with current post data
    POST: Process form and update post

    Requires user to be logged in.
    User must be the author or an admin to edit.

    Args:
        post_id (int): The ID of the post to edit
    """
    # Get post or return 404
    post = BlogService.get_post_by_id(post_id)
    if not post:
        abort(404)

    # Check if user can edit this post
    if not BlogService.can_edit_post(current_user.id, post):
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))

    form = PostForm()

    # Process form submission
    if form.validate_on_submit():
        # Extract form data
        title = form.title.data
        body = form.body.data

        # Call service layer to update post
        success, error = BlogService.update_post(post, title=title, body=body)

        if success:
            flash(f'Post "{post.title}" updated successfully!', 'success')
            return redirect(url_for('blog.view_post', post_id=post.id))
        else:
            flash(f'Failed to update post: {error}', 'danger')

    # Pre-populate form with existing data (GET request)
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body

    return render_template(
        'blog/edit_post.html',
        title='Edit Post',
        form=form,
        post=post
    )


@blog_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Delete a blog post.
    Requires POST request for security (prevents accidental deletion via GET).
    User must be the author or an admin to delete.

    Args:
        post_id (int): The ID of the post to delete
    """
    # Get post or return 404
    post = BlogService.get_post_by_id(post_id)
    if not post:
        abort(404)

    # Check if user can delete this post
    if not BlogService.can_edit_post(current_user.id, post):
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))

    # Store title for flash message before deletion
    post_title = post.title

    # Call service layer to delete post
    success, error = BlogService.delete_post(post)

    if success:
        flash(f'Post "{post_title}" deleted successfully!', 'success')
        return redirect(url_for('blog.index'))
    else:
        flash(f'Failed to delete post: {error}', 'danger')
        return redirect(url_for('blog.view_post', post_id=post_id))


@blog_bp.route('/my-posts')
@login_required
def my_posts():
    """
    Display all posts by the current user.
    Shows user's own posts with pagination.

    Requires user to be logged in.
    """
    # Get page number from query string
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get current user's posts
    result = BlogService.get_posts_by_author(
        author_id=current_user.id,
        page=page,
        per_page=per_page
    )

    return render_template(
        'blog/my_posts.html',
        title='My Posts',
        posts=result['posts'],
        pagination=result
    )


@blog_bp.route('/author/<int:author_id>')
def author_posts(author_id):
    """
    Display all posts by a specific author.
    Shows public view of an author's posts.
    Accessible to everyone.

    Args:
        author_id (int): The ID of the author
    """
    # Import here to avoid circular import
    from app.models import User

    # Get author or return 404
    author = User.query.get(author_id)
    if not author:
        abort(404)

    # Get page number from query string
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Get author's posts
    result = BlogService.get_posts_by_author(
        author_id=author_id,
        page=page,
        per_page=per_page
    )

    return render_template(
        'blog/author_posts.html',
        title=f'Posts by {author.username}',
        author=author,
        posts=result['posts'],
        pagination=result
    )


@blog_bp.route('/search')
def search():
    """
    Search blog posts by title or content.
    Uses query parameter 'q' for search term.
    Accessible to everyone.
    """
    # Get search query from URL parameters
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if not query:
        flash('Please enter a search term.', 'info')
        return redirect(url_for('blog.index'))

    # Search posts
    result = BlogService.search_posts(query=query, page=page, per_page=per_page)

    return render_template(
        'blog/search_results.html',
        title=f'Search Results for "{query}"',
        query=query,
        posts=result['posts'],
        pagination=result
    )


# Error handlers for blog blueprint
@blog_bp.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors within blog blueprint.
    """
    flash('The requested post was not found.', 'warning')
    return redirect(url_for('blog.index'))


@blog_bp.errorhandler(403)
def forbidden(error):
    """
    Handle 403 Forbidden errors within blog blueprint.
    User doesn't have permission for the action.
    """
    flash('You do not have permission to perform this action.', 'danger')
    return redirect(url_for('blog.index'))
