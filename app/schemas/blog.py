from app.extensions import ma
from app.models.post import Post
from marshmallow import fields


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    author_id = fields.Int(required=True)
    created = fields.DateTime(dump_only=True)
    title = fields.Str(required=True)
    body = fields.Str(required=True)

    # Nested relationship
    author = fields.Nested('UserSchema', dump_only=True, exclude=('posts',))


# Instances for serialization
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
