"""
Utility functions package.
Contains helper functions and utilities used across the application.
"""
from datetime import datetime, timezone
import os
import re


def get_current_utc_time():
    """Get the current UTC time."""
    return datetime.now(timezone.utc)


def format_datetime(dt, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Format a datetime object to string.
    
    Args:
        dt: datetime object to format
        format_string: strftime format string
        
    Returns:
        Formatted datetime string or empty string if dt is None
    """
    if dt is None:
        return ''
    return dt.strftime(format_string)


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: String to append when truncated
        
    Returns:
        Truncated text with suffix if truncated
    """
    if text is None:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal attacks.
    
    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for storage
    """
    if not filename:
        return ''

    # Remove any path components
    filename = os.path.basename(filename)

    # Remove any non-alphanumeric characters except dots, dashes, and underscores
    import re
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

    return filename


def allowed_file(filename, allowed_extensions=None):
    """
    Check if a file has an allowed extension.

    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed extensions (without dots)

    Returns:
        True if file extension is allowed, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_profile_image(file, user_id):
    """
    Save a profile image file with a unique filename.

    Args:
        file: FileStorage object from request.files
        user_id: ID of the user (for unique filename)

    Returns:
        Tuple[Optional[str], Optional[str]]: (filename, error_message)
        Returns (filename, None) on success, (None, error_message) on failure
    """
    from flask import current_app
    import uuid

    if not file:
        return None, 'No file provided'

    if file.filename == '':
        return None, 'No file selected'

    # Check file extension
    if not allowed_file(file.filename, current_app.config['ALLOWED_IMAGE_EXTENSIONS']):
        return None, f'Invalid file type. Allowed types: {", ".join(current_app.config["ALLOWED_IMAGE_EXTENSIONS"])}'

    # Get file extension
    ext = file.filename.rsplit('.', 1)[1].lower()

    # Create unique filename: user_{user_id}_{uuid}.{ext}
    unique_filename = f'user_{user_id}_{uuid.uuid4().hex[:8]}.{ext}'

    # Ensure upload directory exists
    profile_images_path = current_app.config['PROFILE_IMAGES_FOLDER']
    os.makedirs(profile_images_path, exist_ok=True)

    # Full path to save the file
    filepath = os.path.join(profile_images_path, unique_filename)

    try:
        # Save the file
        file.save(filepath)
        return unique_filename, None
    except Exception as e:
        return None, f'Failed to save file: {str(e)}'


def delete_profile_image(filename):
    """
    Delete a profile image file.

    Args:
        filename: Name of the file to delete

    Returns:
        bool: True if deleted successfully, False otherwise
    """
    from flask import current_app

    # Don't delete the default image
    if filename == 'default.png' or not filename:
        return True

    filepath = os.path.join(current_app.config['PROFILE_IMAGES_FOLDER'], filename)

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except Exception:
        return False


__all__ = [
    'get_current_utc_time',
    'format_datetime',
    'truncate_text',
    'sanitize_filename',
    'allowed_file',
    'save_profile_image',
    'delete_profile_image'
]
