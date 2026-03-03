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
# url_prefix='/api/v1/blog' means all routes will be prefixed with /api/v1/blog
blog_bp = Blueprint('blog', __name__, url_prefix='/api/v1/blog')


@blog_bp.route('/')
@blog_bp.route('/posts')
def index():
    """
    List All Blog Posts
    Retrieve all blog posts with pagination, ordered by most recent first.
    ---
    tags:
      - Blog
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: Paginated list of blog posts
        schema:
          type: object
          properties:
            posts:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  body:
                    type: string
                  author_id:
                    type: integer
                  created:
                    type: string
                    format: date-time
            total:
              type: integer
              description: Total number of posts
            pages:
              type: integer
              description: Total number of pages
            current_page:
              type: integer
            has_prev:
              type: boolean
            has_next:
              type: boolean
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
    View a Single Blog Post
    Retrieve a blog post by its ID with full content and author details.
    ---
    tags:
      - Blog
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: The unique ID of the blog post
    responses:
      200:
        description: Blog post details
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            body:
              type: string
            author_id:
              type: integer
            created:
              type: string
              format: date-time
            author:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
      404:
        description: Post not found
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
    Create a New Blog Post
    Create a new blog post with a title and body content. Requires authentication.
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    parameters:
      - name: title
        in: formData
        type: string
        required: true
        description: Post title (minimum 3 characters)
        example: My First Blog Post
      - name: body
        in: formData
        type: string
        required: true
        description: Post content (minimum 10 characters)
        example: This is the content of my very first blog post.
    responses:
      200:
        description: Post creation form (GET) or validation error (POST)
      302:
        description: Redirect to the new post on success
      401:
        description: User is not logged in
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
    Edit a Blog Post
    Update an existing blog post's title and/or body. Requires authentication and
    ownership (author or admin).
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: The unique ID of the post to edit
      - name: title
        in: formData
        type: string
        required: true
        description: Updated post title (minimum 3 characters)
      - name: body
        in: formData
        type: string
        required: true
        description: Updated post content (minimum 10 characters)
    responses:
      200:
        description: Edit form with current data (GET) or validation error (POST)
      302:
        description: Redirect to the updated post on success
      401:
        description: User is not logged in
      403:
        description: User does not have permission to edit this post
      404:
        description: Post not found
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
    Delete a Blog Post
    Permanently delete a blog post. Requires authentication and ownership (author or admin).
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: The unique ID of the post to delete
    responses:
      302:
        description: Redirect to blog index on success, or to post on failure
      401:
        description: User is not logged in
      403:
        description: User does not have permission to delete this post
      404:
        description: Post not found
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
    My Posts
    Retrieve all posts authored by the currently logged-in user, with pagination.
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: Paginated list of the current user's posts
      401:
        description: User is not logged in
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
    Posts by Author
    Retrieve all posts by a specific author, with pagination.
    ---
    tags:
      - Blog
    parameters:
      - name: author_id
        in: path
        type: integer
        required: true
        description: The unique ID of the author
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: Paginated list of the author's posts
        schema:
          type: object
          properties:
            author:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
            posts:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  created:
                    type: string
                    format: date-time
      404:
        description: Author not found
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
    Search Blog Posts
    Search for blog posts by title or content using a query string.
    ---
    tags:
      - Blog
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Search term to look for in post titles and content
        example: flask
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
    responses:
      200:
        description: Paginated search results
        schema:
          type: object
          properties:
            query:
              type: string
              description: The search term used
            posts:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  body:
                    type: string
                  created:
                    type: string
                    format: date-time
            total:
              type: integer
      302:
        description: Redirect to blog index if no search term provided
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
