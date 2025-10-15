"""
Comprehensive File Upload Failure Tests
Tests critical file upload failure scenarios including large files, invalid formats, and security scanning failures.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import magic
import hashlib

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
from apps.api.models import APIService
from apps.api.file_upload_security import FileUploadSecurity
from apps.api.enhanced_file_validation import EnhancedFileValidator
from apps.security.models import SecurityPolicy

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class FileUploadSizeFailureTest(EnhancedTransactionTestCase):
    """Test file upload size failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
        self.file_validator = EnhancedFileValidator()
    
    def test_file_too_large_handling(self):
        """Test handling of files that are too large."""
        # Create large file content (simulate 100MB file)
        large_content = b"x" * (100 * 1024 * 1024)  # 100MB
        large_file = SimpleUploadedFile(
            "large_file.txt",
            large_content,
            content_type="text/plain"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_size(large_file, max_size=50 * 1024 * 1024)  # 50MB limit
        
        self.assertIn("File size exceeds maximum allowed size", str(context.exception))
    
    def test_file_size_zero_handling(self):
        """Test handling of zero-size files."""
        empty_file = SimpleUploadedFile(
            "empty_file.txt",
            b"",
            content_type="text/plain"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_size(empty_file, min_size=1)
        
        self.assertIn("File size is too small", str(context.exception))
    
    def test_file_size_negative_handling(self):
        """Test handling of negative file sizes."""
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = -1
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_size(SimpleUploadedFile("test.txt", b"content"), max_size=1024)
            
            self.assertIn("Invalid file size", str(context.exception))
    
    def test_file_size_overflow_handling(self):
        """Test handling of file size overflow."""
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = 2**63  # Very large number
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_size(SimpleUploadedFile("test.txt", b"content"), max_size=1024)
            
            self.assertIn("File size overflow", str(context.exception))
    
    def test_file_size_calculation_error(self):
        """Test handling of file size calculation errors."""
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.side_effect = OSError("File size calculation failed")
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_size(SimpleUploadedFile("test.txt", b"content"), max_size=1024)
            
            self.assertIn("Unable to determine file size", str(context.exception))


class FileUploadFormatFailureTest(EnhancedTransactionTestCase):
    """Test file upload format failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
        self.file_validator = EnhancedFileValidator()
    
    def test_invalid_file_extension_handling(self):
        """Test handling of invalid file extensions."""
        # Create file with invalid extension
        invalid_file = SimpleUploadedFile(
            "malicious.exe",
            b"executable content",
            content_type="application/octet-stream"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_extension(invalid_file, allowed_extensions=['.txt', '.pdf', '.jpg'])
        
        self.assertIn("File extension not allowed", str(context.exception))
    
    def test_missing_file_extension_handling(self):
        """Test handling of files without extensions."""
        # Create file without extension
        no_extension_file = SimpleUploadedFile(
            "file_without_extension",
            b"content",
            content_type="text/plain"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_extension(no_extension_file, allowed_extensions=['.txt', '.pdf'])
        
        self.assertIn("File extension required", str(context.exception))
    
    def test_double_extension_handling(self):
        """Test handling of files with double extensions."""
        # Create file with double extension (potential security risk)
        double_extension_file = SimpleUploadedFile(
            "document.txt.exe",
            b"executable content",
            content_type="application/octet-stream"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_extension(double_extension_file, allowed_extensions=['.txt', '.pdf'])
        
        self.assertIn("Double file extension detected", str(context.exception))
    
    def test_hidden_extension_handling(self):
        """Test handling of files with hidden extensions."""
        # Create file with hidden extension
        hidden_extension_file = SimpleUploadedFile(
            "document.txt\x00.exe",
            b"executable content",
            content_type="application/octet-stream"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_extension(hidden_extension_file, allowed_extensions=['.txt', '.pdf'])
        
        self.assertIn("Hidden file extension detected", str(context.exception))
    
    def test_case_sensitive_extension_handling(self):
        """Test handling of case-sensitive file extensions."""
        # Create file with uppercase extension
        uppercase_extension_file = SimpleUploadedFile(
            "document.TXT",
            b"content",
            content_type="text/plain"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_file_extension(uppercase_extension_file, allowed_extensions=['.txt', '.pdf'])
        
        self.assertIn("File extension not allowed", str(context.exception))
    
    def test_mime_type_mismatch_handling(self):
        """Test handling of MIME type mismatches."""
        # Create file with mismatched MIME type
        mismatched_file = SimpleUploadedFile(
            "document.txt",
            b"executable content",
            content_type="application/octet-stream"  # MIME type doesn't match extension
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_validator.validate_mime_type(mismatched_file, allowed_mime_types=['text/plain'])
        
        self.assertIn("MIME type mismatch", str(context.exception))
    
    def test_magic_number_validation_failure(self):
        """Test handling of magic number validation failures."""
        # Create file with invalid magic number
        invalid_magic_file = SimpleUploadedFile(
            "fake_image.jpg",
            b"not an image",
            content_type="image/jpeg"
        )
        
        with patch('magic.from_buffer') as mock_magic:
            mock_magic.return_value = "ASCII text"
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_magic_number(invalid_magic_file, expected_type="image")
            
            self.assertIn("File type mismatch", str(context.exception))


class FileUploadSecurityFailureTest(EnhancedTransactionTestCase):
    """Test file upload security failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
        self.file_validator = EnhancedFileValidator()
    
    def test_malicious_file_detection(self):
        """Test detection of malicious files."""
        # Create file with malicious content
        malicious_file = SimpleUploadedFile(
            "malicious.txt",
            b"<script>alert('xss')</script>",
            content_type="text/plain"
        )
        
        with self.assertRaises(ValidationError) as context:
            self.file_security.scan_file_security(malicious_file)
        
        self.assertIn("Malicious content detected", str(context.exception))
    
    def test_virus_scanning_failure(self):
        """Test virus scanning failure."""
        # Create file that triggers virus scan failure
        suspicious_file = SimpleUploadedFile(
            "suspicious.exe",
            b"executable content",
            content_type="application/octet-stream"
        )
        
        with patch('apps.api.file_upload_security.virus_scanner') as mock_scanner:
            mock_scanner.scan_file.return_value = False  # Virus detected
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.scan_file_security(suspicious_file)
            
            self.assertIn("Virus detected", str(context.exception))
    
    def test_quarantine_handling(self):
        """Test handling of quarantined files."""
        # Create file that should be quarantined
        quarantined_file = SimpleUploadedFile(
            "quarantined.txt",
            b"quarantined content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.quarantine_manager') as mock_quarantine:
            mock_quarantine.quarantine_file.return_value = True
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.scan_file_security(quarantined_file)
            
            self.assertIn("File quarantined", str(context.exception))
    
    def test_content_filtering_failure(self):
        """Test content filtering failure."""
        # Create file with filtered content
        filtered_file = SimpleUploadedFile(
            "filtered.txt",
            b"spam content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.content_filter') as mock_filter:
            mock_filter.filter_content.return_value = False  # Content filtered
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.scan_file_security(filtered_file)
            
            self.assertIn("Content filtered", str(context.exception))
    
    def test_encryption_detection_failure(self):
        """Test encryption detection failure."""
        # Create encrypted file
        encrypted_file = SimpleUploadedFile(
            "encrypted.txt",
            b"encrypted content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.encryption_detector') as mock_detector:
            mock_detector.is_encrypted.return_value = True
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.scan_file_security(encrypted_file)
            
            self.assertIn("Encrypted file detected", str(context.exception))
    
    def test_metadata_extraction_failure(self):
        """Test metadata extraction failure."""
        # Create file with problematic metadata
        metadata_file = SimpleUploadedFile(
            "metadata.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.metadata_extractor') as mock_extractor:
            mock_extractor.extract_metadata.side_effect = Exception("Metadata extraction failed")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.scan_file_security(metadata_file)
            
            self.assertIn("Metadata extraction failed", str(context.exception))


class FileUploadStorageFailureTest(EnhancedTransactionTestCase):
    """Test file upload storage failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
    
    def test_storage_quota_exceeded_handling(self):
        """Test handling of storage quota exceeded."""
        # Create file that would exceed quota
        large_file = SimpleUploadedFile(
            "large_file.txt",
            b"x" * (1024 * 1024),  # 1MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.check_quota.return_value = False  # Quota exceeded
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.check_storage_quota(large_file, self.organization)
            
            self.assertIn("Storage quota exceeded", str(context.exception))
    
    def test_storage_unavailable_handling(self):
        """Test handling of storage unavailability."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.is_available.return_value = False  # Storage unavailable
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.check_storage_availability(test_file)
            
            self.assertIn("Storage unavailable", str(context.exception))
    
    def test_storage_permission_denied_handling(self):
        """Test handling of storage permission denied."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.has_permission.return_value = False  # Permission denied
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.check_storage_permissions(test_file, self.user)
            
            self.assertIn("Storage permission denied", str(context.exception))
    
    def test_storage_io_error_handling(self):
        """Test handling of storage I/O errors."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.save_file.side_effect = IOError("Storage I/O error")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.save_file(test_file, self.organization)
            
            self.assertIn("Storage I/O error", str(context.exception))
    
    def test_storage_corruption_handling(self):
        """Test handling of storage corruption."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.verify_integrity.return_value = False  # Corruption detected
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.verify_file_integrity(test_file)
            
            self.assertIn("File corruption detected", str(context.exception))


class FileUploadProcessingFailureTest(EnhancedTransactionTestCase):
    """Test file upload processing failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
    
    def test_file_processing_timeout(self):
        """Test handling of file processing timeouts."""
        # Create file that takes too long to process
        large_file = SimpleUploadedFile(
            "large_file.txt",
            b"x" * (10 * 1024 * 1024),  # 10MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.file_processor') as mock_processor:
            mock_processor.process_file.side_effect = TimeoutError("Processing timeout")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.process_file(large_file)
            
            self.assertIn("File processing timeout", str(context.exception))
    
    def test_file_processing_memory_error(self):
        """Test handling of file processing memory errors."""
        # Create file that causes memory issues
        memory_file = SimpleUploadedFile(
            "memory_file.txt",
            b"x" * (100 * 1024 * 1024),  # 100MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.file_processor') as mock_processor:
            mock_processor.process_file.side_effect = MemoryError("Memory limit exceeded")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.process_file(memory_file)
            
            self.assertIn("Memory limit exceeded", str(context.exception))
    
    def test_file_processing_cpu_error(self):
        """Test handling of file processing CPU errors."""
        # Create file that causes CPU issues
        cpu_file = SimpleUploadedFile(
            "cpu_file.txt",
            b"x" * (1024 * 1024),  # 1MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.file_processor') as mock_processor:
            mock_processor.process_file.side_effect = RuntimeError("CPU limit exceeded")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.process_file(cpu_file)
            
            self.assertIn("CPU limit exceeded", str(context.exception))
    
    def test_file_processing_disk_error(self):
        """Test handling of file processing disk errors."""
        # Create file that causes disk issues
        disk_file = SimpleUploadedFile(
            "disk_file.txt",
            b"x" * (1024 * 1024),  # 1MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.file_processor') as mock_processor:
            mock_processor.process_file.side_effect = IOError("Disk space exhausted")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.process_file(disk_file)
            
            self.assertIn("Disk space exhausted", str(context.exception))
    
    def test_file_processing_network_error(self):
        """Test handling of file processing network errors."""
        # Create file that causes network issues
        network_file = SimpleUploadedFile(
            "network_file.txt",
            b"x" * (1024 * 1024),  # 1MB
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.file_processor') as mock_processor:
            mock_processor.process_file.side_effect = ConnectionError("Network error")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.process_file(network_file)
            
            self.assertIn("Network error", str(context.exception))


class FileUploadValidationFailureTest(EnhancedTransactionTestCase):
    """Test file upload validation failure scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_validator = EnhancedFileValidator()
    
    def test_file_hash_validation_failure(self):
        """Test file hash validation failure."""
        # Create file with invalid hash
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.enhanced_file_validation.hashlib') as mock_hashlib:
            mock_hashlib.sha256.return_value.hexdigest.return_value = "invalid_hash"
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_hash(test_file, "expected_hash")
            
            self.assertIn("File hash mismatch", str(context.exception))
    
    def test_file_signature_validation_failure(self):
        """Test file signature validation failure."""
        # Create file with invalid signature
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.enhanced_file_validation.signature_validator') as mock_validator:
            mock_validator.validate_signature.return_value = False
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_signature(test_file)
            
            self.assertIn("File signature invalid", str(context.exception))
    
    def test_file_metadata_validation_failure(self):
        """Test file metadata validation failure."""
        # Create file with invalid metadata
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.enhanced_file_validation.metadata_validator') as mock_validator:
            mock_validator.validate_metadata.return_value = False
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_metadata(test_file)
            
            self.assertIn("File metadata invalid", str(context.exception))
    
    def test_file_content_validation_failure(self):
        """Test file content validation failure."""
        # Create file with invalid content
        test_file = SimpleUploadedFile(
            "test.txt",
            b"invalid content",
            content_type="text/plain"
        )
        
        with patch('apps.api.enhanced_file_validation.content_validator') as mock_validator:
            mock_validator.validate_content.return_value = False
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_content(test_file)
            
            self.assertIn("File content invalid", str(context.exception))
    
    def test_file_structure_validation_failure(self):
        """Test file structure validation failure."""
        # Create file with invalid structure
        test_file = SimpleUploadedFile(
            "test.txt",
            b"invalid structure",
            content_type="text/plain"
        )
        
        with patch('apps.api.enhanced_file_validation.structure_validator') as mock_validator:
            mock_validator.validate_structure.return_value = False
            
            with self.assertRaises(ValidationError) as context:
                self.file_validator.validate_file_structure(test_file)
            
            self.assertIn("File structure invalid", str(context.exception))


class FileUploadRecoveryTest(EnhancedTransactionTestCase):
    """Test file upload recovery scenarios."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.file_security = FileUploadSecurity()
    
    def test_file_upload_retry_mechanism(self):
        """Test file upload retry mechanism."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            # First call fails, second succeeds
            mock_storage.save_file.side_effect = [IOError("Temporary failure"), Mock()]
            
            # Should retry and succeed
            result = self.file_security.save_file(test_file, self.organization)
            self.assertIsNotNone(result)
    
    def test_file_upload_retry_exhaustion(self):
        """Test file upload retry mechanism exhaustion."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.save_file.side_effect = IOError("Persistent failure")
            
            with self.assertRaises(ValidationError) as context:
                self.file_security.save_file(test_file, self.organization)
            
            self.assertIn("File upload failed after retries", str(context.exception))
    
    def test_file_upload_fallback_mechanism(self):
        """Test file upload fallback mechanism."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.save_file.side_effect = IOError("Primary storage failed")
            
            with patch('apps.api.file_upload_security.fallback_storage') as mock_fallback:
                mock_fallback.save_file.return_value = Mock()
                
                # Should use fallback storage
                result = self.file_security.save_file(test_file, self.organization)
                self.assertIsNotNone(result)
    
    def test_file_upload_cleanup_mechanism(self):
        """Test file upload cleanup mechanism."""
        # Create file
        test_file = SimpleUploadedFile(
            "test.txt",
            b"content",
            content_type="text/plain"
        )
        
        with patch('apps.api.file_upload_security.storage_manager') as mock_storage:
            mock_storage.save_file.side_effect = IOError("Storage failed")
            
            with patch('apps.api.file_upload_security.cleanup_manager') as mock_cleanup:
                mock_cleanup.cleanup_file.return_value = True
                
                with self.assertRaises(ValidationError):
                    self.file_security.save_file(test_file, self.organization)
                
                # Should cleanup failed file
                mock_cleanup.cleanup_file.assert_called_once_with(test_file)


# Export test classes
__all__ = [
    'FileUploadSizeFailureTest',
    'FileUploadFormatFailureTest',
    'FileUploadSecurityFailureTest',
    'FileUploadStorageFailureTest',
    'FileUploadProcessingFailureTest',
    'FileUploadValidationFailureTest',
    'FileUploadRecoveryTest'
]