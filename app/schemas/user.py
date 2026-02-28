from app.extensions import ma
from app.models.user import User
from marshmallow import fields


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password',)  # Never expose password in responses

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    posts = fields.Nested('PostSchema', many=True, exclude=('author',), dump_only=True)


class UserCreateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)  # Only for input, never output


# Instances for serialization
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_create_schema = UserCreateSchema()
