import os
from flask import Flask
from dotenv import load_dotenv
from app import config
from app.extensions import db, ma
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # Get database URI from env or use default
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri or db_uri.strip() == '':
            db_uri = f'sqlite:///{os.path.join(app.instance_path, "flaskr.sqlite")}'

        # Load configuration from environment variables
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
            SQLALCHEMY_DATABASE_URI=db_uri,
            SQLALCHEMY_TRACK_MODIFICATIONS=os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() in ('true', '1', 't'),
        )
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from app.models import User, Post

    @app.route('/')
    def index():
        return 'Hello, World!'

    return app
