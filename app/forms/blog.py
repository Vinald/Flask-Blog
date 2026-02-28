"""
Blog/Post forms using Flask-WTF.
Handles input validation for creating and editing blog posts.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    """
    Form for creating and editing blog posts.
    Used for both creation and updates.
    """

    title = StringField(
        'Title',
        validators=[
            DataRequired(message='Title is required'),
            Length(min=3, max=200, message='Title must be between 3 and 200 characters')
        ],
        render_kw={'placeholder': 'Enter post title', 'class': 'form-control'}
    )

    body = TextAreaField(
        'Content',
        validators=[
            DataRequired(message='Content is required'),
            Length(min=10, message='Content must be at least 10 characters')
        ],
        render_kw={
            'placeholder': 'Write your post content here...',
            'class': 'form-control',
            'rows': 10
        }
    )

    submit = SubmitField('Publish', render_kw={'class': 'btn btn-primary'})
