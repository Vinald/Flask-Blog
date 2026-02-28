from app.extensions import db
from datetime import datetime, timezone


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'
