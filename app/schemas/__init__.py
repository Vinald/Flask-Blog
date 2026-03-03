"""
Schemas package.
Contains Marshmallow schemas for serialization/deserialization.
"""
from app.schemas.user import (
    UserSchema, UserPublicSchema, UserCreateSchema,
    user_schema, users_schema, user_public_schema, users_public_schema, user_create_schema
)
from app.schemas.blog import (
    PostSchema, PostCreateSchema, PostUpdateSchema,
    post_schema, posts_schema, post_create_schema, post_update_schema
)

__all__ = [
    # User schemas
    'UserSchema', 'UserPublicSchema', 'UserCreateSchema',
    'user_schema', 'users_schema', 'user_public_schema', 'users_public_schema', 'user_create_schema',
    # Post schemas
    'PostSchema', 'PostCreateSchema', 'PostUpdateSchema',
    'post_schema', 'posts_schema', 'post_create_schema', 'post_update_schema'
]
