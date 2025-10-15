"""
File upload validators for secure file handling.
"""

import os
from django.core.exceptions import ValidationError
from django.conf import settings


# Configuration
ALLOWED_EXTENSIONS = getattr(settings, 'FILE_UPLOAD_ALLOWED_EXTENSIONS', [
    'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'
])
MAX_FILE_SIZE = getattr(settings, 'FILE_UPLOAD_MAX_SIZE', 10 * 1024 * 1024)  # 10MB
DANGEROUS_EXTENSIONS = getattr(settings, 'FILE_UPLOAD_DANGEROUS_EXTENSIONS', [
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 'php', 'asp', 'aspx'
])


def validate_file_extension(file):
    """
    Validate file extension against allowed extensions.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file extension is not allowed
    """
    ext = os.path.splitext(file.name)[1].lower()
    
    # Remove leading dot
    ext = ext[1:] if ext.startswith('.') else ext
    
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '.{ext}' is not allowed. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check for dangerous extensions
    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(
            f"File type '.{ext}' is not allowed for security reasons."
        )
    
    return file


def validate_file_size(file):
    """
    Validate file size against maximum allowed size.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file size exceeds limit
    """
    if file.size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise ValidationError(
            f"File size exceeds {max_size_mb}MB limit. "
            f"Current file size: {file.size / (1024 * 1024):.2f}MB"
        )
    
    return file


def validate_file_upload(file):
    """
    Comprehensive file upload validation.
    
    Validates both file extension and size.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If validation fails
        
    Returns:
        file: The validated file object
    """
    validate_file_extension(file)
    validate_file_size(file)
    return file


def validate_image_file(file):
    """
    Validate image file uploads specifically.
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is not a valid image
        
    Returns:
        file: The validated file object
    """
    allowed_image_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = os.path.splitext(file.name)[1].lower()
    ext = ext[1:] if ext.startswith('.') else ext
    
    if ext not in allowed_image_extensions:
        raise ValidationError(
            f"File type '.{ext}' is not a valid image format. "
            f"Allowed formats: {', '.join(allowed_image_extensions)}"
        )
    
    validate_file_size(file)
    return file
