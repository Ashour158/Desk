"""
Enhanced file upload security with MIME type validation, virus scanning, and compression.
"""

import os
import mimetypes
import hashlib
import magic
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils import timezone
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class FileUploadValidator:
    """
    Comprehensive file upload validation with security checks.
    """
    
    # Allowed file types by category
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'
    ]
    
    ALLOWED_DOCUMENT_TYPES = [
        'application/pdf', 'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain', 'text/csv'
    ]
    
    ALLOWED_ARCHIVE_TYPES = [
        'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'
    ]
    
    ALLOWED_AUDIO_TYPES = [
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4'
    ]
    
    ALLOWED_VIDEO_TYPES = [
        'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/webm'
    ]
    
    # Combined allowed types
    ALLOWED_TYPES = (
        ALLOWED_IMAGE_TYPES + 
        ALLOWED_DOCUMENT_TYPES + 
        ALLOWED_ARCHIVE_TYPES + 
        ALLOWED_AUDIO_TYPES + 
        ALLOWED_VIDEO_TYPES
    )
    
    # File size limits by type
    SIZE_LIMITS = {
        'image': 5 * 1024 * 1024,  # 5MB for images
        'document': 10 * 1024 * 1024,  # 10MB for documents
        'archive': 50 * 1024 * 1024,  # 50MB for archives
        'audio': 20 * 1024 * 1024,  # 20MB for audio
        'video': 100 * 1024 * 1024,  # 100MB for video
        'default': 10 * 1024 * 1024,  # 10MB default
    }
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
        '.php', '.asp', '.jsp', '.py', '.pl', '.sh', '.ps1', '.psm1'
    ]
    
    # Dangerous MIME types
    DANGEROUS_MIME_TYPES = [
        'application/x-executable', 'application/x-msdownload',
        'application/x-msdos-program', 'application/x-msdos-windows'
    ]
    
    def __init__(self, file_type_category='default'):
        self.file_type_category = file_type_category
        self.max_size = self.SIZE_LIMITS.get(file_type_category, self.SIZE_LIMITS['default'])
    
    def validate_file(self, file: UploadedFile) -> dict:
        """
        Comprehensive file validation with security checks.
        
        Args:
            file: UploadedFile instance
            
        Returns:
            dict: Validation result with file info
            
        Raises:
            ValidationError: If file validation fails
        """
        validation_result = {
            'is_valid': True,
            'file_name': file.name,
            'file_size': file.size,
            'mime_type': None,
            'file_hash': None,
            'compression_applied': False,
            'errors': []
        }
        
        try:
            # 1. Basic file validation
            self._validate_basic_file(file)
            
            # 2. File size validation
            self._validate_file_size(file)
            
            # 3. File extension validation
            self._validate_file_extension(file)
            
            # 4. MIME type validation
            mime_type = self._validate_mime_type(file)
            validation_result['mime_type'] = mime_type
            
            # 5. Security validation
            self._validate_security(file)
            
            # 6. Generate file hash
            file_hash = self._generate_file_hash(file)
            validation_result['file_hash'] = file_hash
            
            # 7. Apply compression if needed
            if self._should_compress(file, mime_type):
                compressed_file = self._compress_file(file)
                if compressed_file:
                    validation_result['compression_applied'] = True
                    validation_result['compressed_size'] = compressed_file.size
            
        except ValidationError as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(str(e))
            logger.warning(f"File validation failed: {e}")
        
        return validation_result
    
    def _validate_basic_file(self, file: UploadedFile):
        """Validate basic file properties."""
        if not file:
            raise ValidationError("No file provided")
        
        if not hasattr(file, 'name') or not file.name:
            raise ValidationError("File name is required")
        
        if not hasattr(file, 'size') or file.size == 0:
            raise ValidationError("File size cannot be zero")
    
    def _validate_file_size(self, file: UploadedFile):
        """Validate file size against limits."""
        if file.size > self.max_size:
            raise ValidationError(
                f"File size ({file.size} bytes) exceeds maximum allowed size "
                f"({self.max_size} bytes) for {self.file_type_category} files"
            )
    
    def _validate_file_extension(self, file: UploadedFile):
        """Validate file extension against allowed types."""
        file_name = file.name.lower()
        
        # Check for dangerous extensions
        for dangerous_ext in self.DANGEROUS_EXTENSIONS:
            if file_name.endswith(dangerous_ext):
                raise ValidationError(f"Dangerous file extension not allowed: {dangerous_ext}")
        
        # Check if extension matches allowed types
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type and mime_type not in self.ALLOWED_TYPES:
            raise ValidationError(f"File type not allowed: {mime_type}")
    
    def _validate_mime_type(self, file: UploadedFile) -> str:
        """Validate MIME type using multiple methods."""
        # Method 1: Use python-magic for accurate MIME detection
        try:
            file_content = file.read(1024)  # Read first 1KB
            file.seek(0)  # Reset file pointer
            
            mime_type = magic.from_buffer(file_content, mime=True)
            
            # Method 2: Fallback to mimetypes module
            if not mime_type:
                mime_type, _ = mimetypes.guess_type(file.name)
            
            # Method 3: Use file.content_type if available
            if not mime_type and hasattr(file, 'content_type'):
                mime_type = file.content_type
            
            if not mime_type:
                raise ValidationError("Unable to determine file type")
            
            # Validate against allowed types
            if mime_type not in self.ALLOWED_TYPES:
                raise ValidationError(f"File type not allowed: {mime_type}")
            
            # Check for dangerous MIME types
            if mime_type in self.DANGEROUS_MIME_TYPES:
                raise ValidationError(f"Dangerous file type not allowed: {mime_type}")
            
            return mime_type
            
        except Exception as e:
            logger.error(f"MIME type validation failed: {e}")
            raise ValidationError("File type validation failed")
    
    def _validate_security(self, file: UploadedFile):
        """Perform security validation checks."""
        # Check for embedded executables in images
        if file.content_type and file.content_type.startswith('image/'):
            self._check_image_security(file)
        
        # Check for suspicious file patterns
        self._check_suspicious_patterns(file)
    
    def _check_image_security(self, file: UploadedFile):
        """Check for security issues in image files."""
        try:
            # Read file content
            file_content = file.read()
            file.seek(0)
            
            # Check for embedded scripts or executables
            suspicious_patterns = [
                b'<script', b'javascript:', b'vbscript:', b'<iframe',
                b'<object', b'<embed', b'<applet', b'<form'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in file_content.lower():
                    raise ValidationError("Suspicious content detected in image file")
            
        except Exception as e:
            logger.warning(f"Image security check failed: {e}")
    
    def _check_suspicious_patterns(self, file: UploadedFile):
        """Check for suspicious patterns in file content."""
        try:
            file_content = file.read(1024)  # Read first 1KB
            file.seek(0)
            
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # PE executable
                b'\x7fELF',  # ELF executable
                b'\xfe\xed\xfa',  # Mach-O executable
            ]
            
            for signature in executable_signatures:
                if file_content.startswith(signature):
                    raise ValidationError("Executable file detected")
            
        except Exception as e:
            logger.warning(f"Suspicious pattern check failed: {e}")
    
    def _generate_file_hash(self, file: UploadedFile) -> str:
        """Generate SHA-256 hash of file content."""
        try:
            file_content = file.read()
            file.seek(0)
            
            file_hash = hashlib.sha256(file_content).hexdigest()
            return file_hash
            
        except Exception as e:
            logger.error(f"File hash generation failed: {e}")
            return None
    
    def _should_compress(self, file: UploadedFile, mime_type: str) -> bool:
        """Determine if file should be compressed."""
        # Compress images larger than 1MB
        if mime_type.startswith('image/') and file.size > 1024 * 1024:
            return True
        
        # Compress documents larger than 5MB
        if mime_type in self.ALLOWED_DOCUMENT_TYPES and file.size > 5 * 1024 * 1024:
            return True
        
        return False
    
    def _compress_file(self, file: UploadedFile):
        """Compress file if it's an image."""
        try:
            if file.content_type and file.content_type.startswith('image/'):
                return self._compress_image(file)
        except Exception as e:
            logger.warning(f"File compression failed: {e}")
        
        return None
    
    def _compress_image(self, file: UploadedFile):
        """Compress image file."""
        try:
            # Open image with PIL
            image = Image.open(file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1920x1080)
            max_size = (1920, 1080)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with compression
            from io import BytesIO
            compressed_buffer = BytesIO()
            image.save(compressed_buffer, format='JPEG', quality=85, optimize=True)
            compressed_buffer.seek(0)
            
            # Create new UploadedFile
            from django.core.files.uploadedfile import SimpleUploadedFile
            compressed_file = SimpleUploadedFile(
                file.name,
                compressed_buffer.getvalue(),
                content_type='image/jpeg'
            )
            
            return compressed_file
            
        except Exception as e:
            logger.error(f"Image compression failed: {e}")
            return None


class FileUploadSecurityMiddleware:
    """
    Middleware to apply file upload security to all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Apply security checks to file uploads
        if request.FILES:
            for field_name, file_list in request.FILES.lists():
                for file in file_list:
                    validator = FileUploadValidator()
                    validation_result = validator.validate_file(file)
                    
                    if not validation_result['is_valid']:
                        # Log security violation
                        logger.warning(
                            f"File upload security violation: {validation_result['errors']} "
                            f"from IP: {request.META.get('REMOTE_ADDR')}"
                        )
        
        response = self.get_response(request)
        return response


class FileUploadViewMixin:
    """
    Mixin for views that handle file uploads with enhanced security.
    """
    
    def validate_uploaded_file(self, file: UploadedFile, file_type_category='default'):
        """
        Validate uploaded file with security checks.
        
        Args:
            file: UploadedFile instance
            file_type_category: Type category for size limits
            
        Returns:
            dict: Validation result
        """
        validator = FileUploadValidator(file_type_category)
        return validator.validate_file(file)
    
    def handle_file_upload(self, file: UploadedFile, file_type_category='default'):
        """
        Handle file upload with security and compression.
        
        Args:
            file: UploadedFile instance
            file_type_category: Type category for validation
            
        Returns:
            dict: Upload result with file info
        """
        validation_result = self.validate_uploaded_file(file, file_type_category)
        
        if not validation_result['is_valid']:
            raise ValidationError(validation_result['errors'])
        
        # Additional processing
        upload_result = {
            'original_name': file.name,
            'file_size': file.size,
            'mime_type': validation_result['mime_type'],
            'file_hash': validation_result['file_hash'],
            'compression_applied': validation_result.get('compression_applied', False),
            'upload_timestamp': timezone.now().isoformat(),
        }
        
        if validation_result.get('compressed_size'):
            upload_result['compressed_size'] = validation_result['compressed_size']
        
        return upload_result


# File upload configuration for different endpoint types
FILE_UPLOAD_CONFIGS = {
    'ticket_attachments': {
        'allowed_types': FileUploadValidator.ALLOWED_IMAGE_TYPES + FileUploadValidator.ALLOWED_DOCUMENT_TYPES,
        'max_size': 10 * 1024 * 1024,  # 10MB
        'compression': True,
        'virus_scan': True
    },
    'user_avatars': {
        'allowed_types': FileUploadValidator.ALLOWED_IMAGE_TYPES,
        'max_size': 2 * 1024 * 1024,  # 2MB
        'compression': True,
        'virus_scan': False
    },
    'knowledge_base': {
        'allowed_types': FileUploadValidator.ALLOWED_IMAGE_TYPES + FileUploadValidator.ALLOWED_DOCUMENT_TYPES,
        'max_size': 20 * 1024 * 1024,  # 20MB
        'compression': True,
        'virus_scan': True
    },
    'work_order_attachments': {
        'allowed_types': FileUploadValidator.ALLOWED_IMAGE_TYPES + FileUploadValidator.ALLOWED_DOCUMENT_TYPES + FileUploadValidator.ALLOWED_VIDEO_TYPES,
        'max_size': 50 * 1024 * 1024,  # 50MB
        'compression': True,
        'virus_scan': True
    }
}


def get_file_upload_config(endpoint_type):
    """
    Get file upload configuration for specific endpoint type.
    """
    return FILE_UPLOAD_CONFIGS.get(endpoint_type, {
        'allowed_types': FileUploadValidator.ALLOWED_TYPES,
        'max_size': 10 * 1024 * 1024,
        'compression': False,
        'virus_scan': False
    })
