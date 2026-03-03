"""
Blog JSON API routes.
Returns JSON responses for Swagger UI documentation and API consumers.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.services.blog_service import BlogService

# JSON API blueprint at /api/v1/blog
blog_api_bp = Blueprint('blog_api', __name__, url_prefix='/api/v1/blog')


def _serialize_post(post):
    """Serialize a Post object to a dictionary."""
    return {
        'id': post.id,
        'title': post.title,
        'body': post.body,
        'author_id': post.author_id,
        'created': post.created.isoformat() if post.created else None,
        'author': {
            'id': post.author.id,
            'username': post.author.username,
        } if post.author else None,
    }


def _pagination_response(result, posts_key='posts'):
    """Build a standard pagination response."""
    return {
        posts_key: [_serialize_post(p) for p in result['posts']],
        'total': result['total'],
        'pages': result['pages'],
        'current_page': result['current_page'],
        'has_prev': result['has_prev'],
        'has_next': result['has_next'],
    }


@blog_api_bp.route('/posts', methods=['GET'])
def list_posts():
    """
    List All Blog Posts
    Retrieve all blog posts with pagination, ordered by most recent first.
    ---
    tags:
      - Blog
    produces:
      - application/json
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Page number for pagination
      - name: per_page
        in: query
        type: integer
        required: false
        default: 10
        description: Number of posts per page
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
                  author:
                    type: object
                    properties:
                      id:
                        type: integer
                      username:
                        type: string
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
            has_prev:
              type: boolean
            has_next:
              type: boolean
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = BlogService.get_all_posts(page=page, per_page=per_page)
    return jsonify(_pagination_response(result)), 200


@blog_api_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get a Single Blog Post
    Retrieve a blog post by its ID with full content and author details.
    ---
    tags:
      - Blog
    produces:
      - application/json
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
    post = BlogService.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    return jsonify(_serialize_post(post)), 200


@blog_api_bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    """
    Create a New Blog Post
    Create a new blog post with a title and body. Requires authentication.
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - body
          properties:
            title:
              type: string
              description: Post title (minimum 3 characters)
              example: My First Blog Post
            body:
              type: string
              description: Post content (minimum 10 characters)
              example: This is the content of my very first blog post.
    responses:
      201:
        description: Post created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            post:
              type: object
              properties:
                id:
                  type: integer
                title:
                  type: string
      400:
        description: Validation error
      401:
        description: User is not logged in
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    title = data.get('title', '').strip()
    body = data.get('body', '').strip()

    if not title or not body:
        return jsonify({'error': 'Title and body are required'}), 400

    post, error = BlogService.create_post(
        author_id=current_user.id,
        title=title,
        body=body
    )

    if post:
        return jsonify({
            'message': f'Post "{post.title}" created successfully',
            'post': _serialize_post(post),
        }), 201
    else:
        return jsonify({'error': error}), 400


@blog_api_bp.route('/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """
    Update a Blog Post
    Update an existing blog post's title and/or body. Requires authentication
    and ownership (author or admin).
    ---
    tags:
      - Blog
    security:
      - SessionAuth: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: The unique ID of the post to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: Updated post title
            body:
              type: string
              description: Updated post content
    responses:
      200:
        description: Post updated successfully
      400:
        description: Validation error
      401:
        description: User is not logged in
      403:
        description: User does not have permission to edit this post
      404:
        description: Post not found
    """
    post = BlogService.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if not BlogService.can_edit_post(current_user.id, post):
        return jsonify({'error': 'You do not have permission to edit this post'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    title = data.get('title')
    body = data.get('body')

    success, error = BlogService.update_post(post, title=title, body=body)

    if success:
        return jsonify({
            'message': f'Post "{post.title}" updated successfully',
            'post': _serialize_post(post),
        }), 200
    else:
        return jsonify({'error': error}), 400


@blog_api_bp.route('/posts/<int:post_id>', methods=['DELETE'])
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
    produces:
      - application/json
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: The unique ID of the post to delete
    responses:
      200:
        description: Post deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      401:
        description: User is not logged in
      403:
        description: User does not have permission to delete this post
      404:
        description: Post not found
    """
    post = BlogService.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if not BlogService.can_edit_post(current_user.id, post):
        return jsonify({'error': 'You do not have permission to delete this post'}), 403

    post_title = post.title
    success, error = BlogService.delete_post(post)

    if success:
        return jsonify({'message': f'Post "{post_title}" deleted successfully'}), 200
    else:
        return jsonify({'error': error}), 400


@blog_api_bp.route('/my-posts', methods=['GET'])
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
    produces:
      - application/json
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = BlogService.get_posts_by_author(
        author_id=current_user.id,
        page=page,
        per_page=per_page
    )
    return jsonify(_pagination_response(result)), 200


@blog_api_bp.route('/author/<int:author_id>', methods=['GET'])
def author_posts(author_id):
    """
    Posts by Author
    Retrieve all posts by a specific author, with pagination.
    ---
    tags:
      - Blog
    produces:
      - application/json
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
      404:
        description: Author not found
    """
    from app.models import User
    author = User.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = BlogService.get_posts_by_author(
        author_id=author_id,
        page=page,
        per_page=per_page
    )

    response = _pagination_response(result)
    response['author'] = {'id': author.id, 'username': author.username}
    return jsonify(response), 200


@blog_api_bp.route('/search', methods=['GET'])
def search():
    """
    Search Blog Posts
    Search for blog posts by title or content using a query string.
    ---
    tags:
      - Blog
    produces:
      - application/json
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
            posts:
              type: array
              items:
                type: object
            total:
              type: integer
      400:
        description: Search query is required
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Search query parameter "q" is required'}), 400

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    result = BlogService.search_posts(query=query, page=page, per_page=per_page)

    response = _pagination_response(result)
    response['query'] = query
    return jsonify(response), 200
