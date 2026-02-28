from app.extensions import db, bcrypt, login_manager
from datetime import datetime, timezone
from flask_login import UserMixin


class User(UserMixin, db.Model):
    """
    User model for authentication and authorization.
    Inherits from UserMixin to get Flask-Login authentication methods.
    """
    __tablename__ = 'user'

    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # User status fields
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        """
        Prevent password from being accessed directly.
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        Hash password when setting it.
        Uses bcrypt for secure password hashing.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """
        Verify a password against the stored hash.

        Args:
            password (str): The password to check

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """
        Update the last login timestamp.
        Called after successful authentication.
        """
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    # Flask-Login required methods (inherited from UserMixin)
    # - is_authenticated: Always returns True for authenticated users
    # - is_active: Returns the is_active field value
    # - is_anonymous: Always returns False for registered users
    # - get_id(): Returns the user ID as a string


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.
    This is called to reload the user object from the user ID stored in the session.

    Args:
        user_id (str): The user ID as a unicode string

    Returns:
        User: The user object or None if user doesn't exist
    """
    return User.query.get(int(user_id))
