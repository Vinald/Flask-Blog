"""
Utility functions package.
Contains helper functions and utilities used across the application.
"""
from datetime import datetime, timezone


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
        Sanitized filename safe for filesystem use
    """
    import re
    # Remove any directory components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove any non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^\w\-.]', '', filename)
    return filename


__all__ = [
    'get_current_utc_time',
    'format_datetime',
    'truncate_text',
    'sanitize_filename'
]
