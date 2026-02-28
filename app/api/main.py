tab"""
Main blueprint - handles general application routes.
Includes home page, about page, etc.
"""
from flask import Blueprint, render_template
from flask_login import current_user

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """
    Home page route.
    Displays welcome message and navigation based on authentication status.
    """
    return render_template('index.html', title='Home')


@main_bp.route('/about')
def about():
    """
    About page route.
    """
    return render_template('about.html', title='About')
