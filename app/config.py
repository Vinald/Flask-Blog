"""
Application configuration settings.

This module contains configuration classes for different environments.
Configuration is loaded based on the FLASK_ENV environment variable.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class with default settings."""
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTForms
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Pagination
    POSTS_PER_PAGE = 10
    
    # File uploads (if needed in future)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///instance/flaskr.sqlite'
    )


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Require SECRET_KEY in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    # PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True


# Configuration dictionary for easy lookup
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the appropriate configuration class based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
