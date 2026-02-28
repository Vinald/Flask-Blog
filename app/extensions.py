"""
Flask extensions initialization.
All extensions are initialized here and then registered with the app in app/auth.py
"""
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Database ORM
db = SQLAlchemy()

# Serialization/Deserialization
ma = Marshmallow()

# Authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to login page if not authenticated
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Password hashing
bcrypt = Bcrypt()
