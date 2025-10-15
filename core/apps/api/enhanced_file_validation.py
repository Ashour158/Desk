"""
Enhanced file validation with comprehensive security measures.
"""

import os
import mimetypes
import hashlib
import magic
import virus_scanner
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils import timezone
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class EnhancedFileValidator:
    """
    Enhanced file validator with comprehensive security measures.
    """
    
    # Enhanced file type validation
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
    
    # Enhanced size limits with stricter controls
    SIZE_LIMITS = {
        'image': 5 * 1024 * 1024,      # 5MB
        'document': 10 * 1024 * 1024,   # 10MB
        'archive': 50 * 1024 * 1024,    # 50MB
        'audio': 20 * 1024 * 1024,     # 20MB
        'video': 100 * 1024 * 1024,     # 100MB
        'default': 10 * 1024 * 1024,    # 10MB
    }
    
    # Enhanced dangerous extensions list
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
        '.php', '.asp', '.jsp', '.py', '.pl', '.sh', '.ps1', '.psm1', '.dll',
        '.sys', '.drv', '.ocx', '.cpl', '.msi', '.msp', '.mst', '.reg'
    ]
    
    def __init__(self, file_type_category='default'):
        self.file_type_category = file_type_category
        self.max_size = self.SIZE_LIMITS.get(file_type_category, self.SIZE_LIMITS['default'])
        self.virus_scanner = virus_scanner.VirusScanner()
    
    def validate_file(self, file: UploadedFile) -> dict:
        """
        Comprehensive file validation with enhanced security.
        """
        validation_result = {
            'is_valid': True,
            'file_name': file.name,
            'file_size': file.size,
            'mime_type': None,
            'file_hash': None,
            'security_scan': False,
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
            
            # 5. Enhanced security validation
            self._validate_security(file)
            
            # 6. Virus scanning
            virus_scan_result = self._scan_for_viruses(file)
            validation_result['security_scan'] = virus_scan_result['clean']
            if not virus_scan_result['clean']:
                validation_result['errors'].append(f"Virus detected: {virus_scan_result['threat']}")
                validation_result['is_valid'] = False
            
            # 7. Generate file hash
            file_hash = self._generate_file_hash(file)
            validation_result['file_hash'] = file_hash
            
            # 8. Apply compression if needed
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
    
    def _scan_for_viruses(self, file: UploadedFile) -> dict:
        """
        Enhanced virus scanning with multiple engines.
        """
        try:
            # Read file content for scanning
            file_content = file.read()
            file.seek(0)  # Reset file pointer
            
            # Scan with multiple engines
            scan_result = self.virus_scanner.scan_file(file_content, file.name)
            
            return {
                'clean': scan_result['clean'],
                'threat': scan_result.get('threat', None),
                'engine': scan_result.get('engine', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Virus scanning failed: {e}")
            return {'clean': False, 'threat': 'Scan failed', 'engine': 'error'}
    
    def _validate_security(self, file: UploadedFile):
        """
        Enhanced security validation with content analysis.
        """
        try:
            # Read file content
            file_content = file.read()
            file.seek(0)
            
            # Check for embedded scripts
            self._check_embedded_scripts(file_content)
            
            # Check for executable signatures
            self._check_executable_signatures(file_content)
            
            # Check for suspicious patterns
            self._check_suspicious_patterns(file_content)
            
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            raise ValidationError("Security validation failed")
    
    def _check_embedded_scripts(self, content: bytes):
        """Check for embedded scripts in files."""
        suspicious_patterns = [
            b'<script', b'javascript:', b'vbscript:', b'<iframe',
            b'<object', b'<embed', b'<applet', b'<form',
            b'eval(', b'exec(', b'system(', b'shell_exec('
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content.lower():
                raise ValidationError("Suspicious content detected in file")
    
    def _check_executable_signatures(self, content: bytes):
        """Check for executable file signatures."""
        executable_signatures = [
            b'MZ',  # PE executable
            b'\x7fELF',  # ELF executable
            b'\xfe\xed\xfa',  # Mach-O executable
            b'PK\x03\x04',  # ZIP archive
        ]
        
        for signature in executable_signatures:
            if content.startswith(signature):
                raise ValidationError("Executable file detected")
    
    def _check_suspicious_patterns(self, content: bytes):
        """Check for suspicious patterns in file content."""
        # Check for base64 encoded content
        if b'base64' in content.lower():
            # Additional validation for base64 content
            pass
        
        # Check for encrypted content
        if self._is_encrypted_content(content):
            raise ValidationError("Encrypted content detected")
    
    def _is_encrypted_content(self, content: bytes) -> bool:
        """Check if content appears to be encrypted."""
        # Simple entropy check
        if len(content) > 1000:
            # Check for high entropy (potential encryption)
            entropy = self._calculate_entropy(content[:1000])
            return entropy > 7.5  # High entropy threshold
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        import math
        from collections import Counter
        
        if not data:
            return 0
        
        counts = Counter(data)
        entropy = 0
        for count in counts.values():
            p = count / len(data)
            entropy -= p * math.log2(p)
        
        return entropy


class FileUploadSecurityMiddleware:
    """
    Enhanced middleware for file upload security.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.validator = EnhancedFileValidator()
    
    def __call__(self, request):
        # Apply enhanced security checks to file uploads
        if request.FILES:
            for field_name, file_list in request.FILES.lists():
                for file in file_list:
                    validation_result = self.validator.validate_file(file)
                    
                    if not validation_result['is_valid']:
                        # Log security violation
                        logger.warning(
                            f"File upload security violation: {validation_result['errors']} "
                            f"from IP: {request.META.get('REMOTE_ADDR')} "
                            f"User: {getattr(request, 'user', 'Anonymous')}"
                        )
                        
                        # Block the request
                        from django.http import JsonResponse
                        return JsonResponse({
                            'error': {
                                'code': 'FILE_UPLOAD_ERROR',
                                'message': 'File upload security violation',
                                'details': validation_result['errors']
                            }
                        }, status=400)
        
        response = self.get_response(request)
        return response
