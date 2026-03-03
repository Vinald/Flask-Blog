"""
Blog post schemas for serialization/deserialization.
"""
from app.extensions import ma
from app.models.post import Post
from marshmallow import fields, validate


class PostSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing Post objects."""
    
    class Meta:
        model = Post
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    author_id = fields.Int(required=True)
    created = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200)
    )
    body = fields.Str(
        required=True,
        validate=validate.Length(min=10)
    )

    # Nested relationship
    author = fields.Nested('UserSchema', dump_only=True, exclude=('posts', 'email'))
    
    # Computed fields
    excerpt = fields.Str(dump_only=True)
    was_edited = fields.Bool(dump_only=True)


class PostCreateSchema(ma.Schema):
    """Schema for creating new posts."""
    
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200, error='Title must be between 3 and 200 characters')
    )
    body = fields.Str(
        required=True,
        validate=validate.Length(min=10, error='Content must be at least 10 characters')
    )


class PostUpdateSchema(ma.Schema):
    """Schema for updating posts."""
    
    title = fields.Str(
        validate=validate.Length(min=3, max=200, error='Title must be between 3 and 200 characters')
    )
    body = fields.Str(
        validate=validate.Length(min=10, error='Content must be at least 10 characters')
    )


# Instances for serialization
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
post_create_schema = PostCreateSchema()
post_update_schema = PostUpdateSchema()
