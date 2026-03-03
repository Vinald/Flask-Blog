"""
Post model for blog posts.
"""
from app.extensions import db
from datetime import datetime, timezone


class Post(db.Model):
    """
    Blog post model.
    Contains the content and metadata for blog posts.
    """
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    
    # Timestamps
    created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Post {self.id}: {self.title[:30]}>'

    @property
    def excerpt(self):
        """Return a short excerpt of the post body."""
        max_length = 150
        if len(self.body) <= max_length:
            return self.body
        return self.body[:max_length].rsplit(' ', 1)[0] + '...'

    @property
    def was_edited(self):
        """Check if the post was edited after creation."""
        return self.updated_at is not None
