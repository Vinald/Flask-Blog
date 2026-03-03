"""
User schemas for serialization/deserialization.
"""
from app.extensions import ma
from app.models.user import User
from marshmallow import fields, validate


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing User objects."""
    
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)  # Never expose password in responses

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(dump_only=True)  # Only show email to authenticated users
    is_active = fields.Bool(dump_only=True)
    is_admin = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    
    # Relationship
    posts = fields.Nested('PostSchema', many=True, exclude=('author',), dump_only=True)
    
    # Computed field
    post_count = fields.Method('get_post_count', dump_only=True)
    
    def get_post_count(self, obj):
        """Get the number of posts by this user."""
        return len(obj.posts) if obj.posts else 0


class UserPublicSchema(ma.SQLAlchemyAutoSchema):
    """Schema for public user data (excludes sensitive fields)."""
    
    class Meta:
        model = User
        load_instance = True
        fields = ('id', 'username', 'created_at')

    id = fields.Int(dump_only=True)
    username = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(ma.Schema):
    """Schema for user registration."""
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error='Username must be between 3 and 80 characters'),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error='Username must contain only letters, numbers, and underscores')
        ]
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, error='Password must be at least 8 characters')
    )


# Instances for serialization
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_public_schema = UserPublicSchema()
users_public_schema = UserPublicSchema(many=True)
user_create_schema = UserCreateSchema()
