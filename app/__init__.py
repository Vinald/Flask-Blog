import os
from flask import Flask
from dotenv import load_dotenv
from app import config
from app.extensions import db, ma, login_manager, bcrypt
from flask_migrate import Migrate
from flasgger import Swagger
from app.swagger_config import SWAGGER_CONFIG, SWAGGER_TEMPLATE

# Load environment variables from .env file
load_dotenv()

migrate = Migrate()

def create_app(test_config=None):
    """
    Application factory pattern.
    Creates and configures the Flask application.

    Args:
        test_config (dict): Optional test configuration

    Returns:
        Flask: Configured Flask application instance
    """
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
            # WTForms configuration
            WTF_CSRF_ENABLED=True,
            WTF_CSRF_TIME_LIMIT=None,  # No time limit for CSRF token
        )
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Import models to ensure they're registered with SQLAlchemy
    # This must be done before registering blueprints to avoid circular imports
    with app.app_context():
        from app.models import User, Post

    # Register blueprints
    from app.api.v1.auth import auth_bp
    from app.api.v1.main import main_bp
    from app.api.v1.blog import blog_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp)

    # Initialize Swagger UI documentation
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

    # Context processor to make utilities available in all templates
    @app.context_processor
    def inject_utilities():
        """
        Make useful utilities available in all templates:
        - current_user: The currently logged-in user
        - datetime: Python datetime module for date operations
        - now: Current datetime function
        """
        from flask_login import current_user
        from datetime import datetime, timezone
        return dict(
            current_user=current_user,
            datetime=datetime,
            now=lambda: datetime.now(timezone.utc)
        )

    return app
