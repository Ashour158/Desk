"""
Input sanitization utilities for user-generated content.
"""

import re
from django.utils.html import escape, strip_tags


def sanitize_html(text, allowed_tags=None, allowed_attributes=None):
    """
    Sanitize HTML content by removing dangerous tags and attributes.
    
    Args:
        text (str): HTML content to sanitize
        allowed_tags (list): List of allowed HTML tags (default: safe tags)
        allowed_attributes (dict): Dict of allowed attributes per tag
        
    Returns:
        str: Sanitized HTML content
    """
    if not text:
        return text
    
    # Default allowed tags for rich text
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li', 'h1', 'h2', 'h3']
    
    # Default allowed attributes
    if allowed_attributes is None:
        allowed_attributes = {
            'a': ['href', 'title'],
        }
    
    try:
        import bleach
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    except ImportError:
        # Fallback to basic sanitization if bleach is not installed
        return strip_tags(text)


def sanitize_plain_text(text):
    """
    Sanitize plain text input by removing HTML and escaping special characters.
    
    Args:
        text (str): Text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return text
    
    # Remove all HTML tags
    text = strip_tags(text)
    
    # Escape HTML special characters
    text = escape(text)
    
    return text


def sanitize_sql_like_pattern(pattern):
    """
    Sanitize SQL LIKE pattern by escaping special characters.
    
    Args:
        pattern (str): LIKE pattern to sanitize
        
    Returns:
        str: Sanitized pattern
    """
    if not pattern:
        return pattern
    
    # Escape SQL LIKE special characters
    pattern = pattern.replace('\\', '\\\\')
    pattern = pattern.replace('%', r'\%')
    pattern = pattern.replace('_', r'\_')
    
    return pattern


def sanitize_filename(filename):
    """
    Sanitize filename by removing dangerous characters.
    
    Args:
        filename (str): Filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return filename
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Remove multiple dots (path traversal)
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    
    return filename


def sanitize_url(url):
    """
    Sanitize URL to prevent XSS and other attacks.
    
    Args:
        url (str): URL to sanitize
        
    Returns:
        str: Sanitized URL or empty string if invalid
    """
    if not url:
        return url
    
    # Remove whitespace
    url = url.strip()
    
    # Block javascript: and data: protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    url_lower = url.lower()
    
    for protocol in dangerous_protocols:
        if url_lower.startswith(protocol):
            return ''
    
    # Only allow http, https, and relative URLs
    if not (url.startswith(('http://', 'https://', '/', '#'))):
        return ''
    
    return url


def sanitize_email(email):
    """
    Basic email sanitization and validation.
    
    Args:
        email (str): Email address to sanitize
        
    Returns:
        str: Sanitized email or empty string if invalid
    """
    if not email:
        return email
    
    # Remove whitespace
    email = email.strip()
    
    # Basic email pattern validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return ''
    
    return email.lower()


def sanitize_search_query(query):
    """
    Sanitize search query to prevent injection attacks.
    
    Args:
        query (str): Search query to sanitize
        
    Returns:
        str: Sanitized query
    """
    if not query:
        return query
    
    # Remove HTML tags
    query = strip_tags(query)
    
    # Remove excessive whitespace
    query = ' '.join(query.split())
    
    # Limit length
    max_length = 200
    if len(query) > max_length:
        query = query[:max_length]
    
    return query
