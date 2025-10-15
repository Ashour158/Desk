"""
Database Backup Encryption System.
"""

import os
import gzip
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

logger = logging.getLogger(__name__)


class BackupEncryption:
    """
    Database backup encryption system.
    """
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.backup_dir = getattr(settings, 'BACKUP_DIR', '/tmp/backups')
        self.retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        self.compression_enabled = getattr(settings, 'BACKUP_COMPRESSION', True)
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key."""
        key = os.environ.get('BACKUP_ENCRYPTION_KEY')
        if not key:
            # Generate key from SECRET_KEY
            password = settings.SECRET_KEY.encode()
            salt = b'backup_salt_2024'  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = key.encode()
        return key
    
    def create_encrypted_backup(self, database_name: str = None) -> Tuple[bool, str]:
        """Create encrypted database backup."""
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"backup_{timestamp}.sql"
            encrypted_filename = f"backup_{timestamp}.sql.enc"
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_backup_path = os.path.join(temp_dir, backup_filename)
                
                # Create database dump
                if not self._create_database_dump(temp_backup_path, database_name):
                    return False, "Failed to create database dump"
                
                # Compress backup if enabled
                if self.compression_enabled:
                    compressed_path = f"{temp_backup_path}.gz"
                    with open(temp_backup_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    temp_backup_path = compressed_path
                
                # Encrypt backup
                encrypted_path = os.path.join(self.backup_dir, encrypted_filename)
                if not self._encrypt_file(temp_backup_path, encrypted_path):
                    return False, "Failed to encrypt backup"
                
                # Verify encrypted backup
                if not self._verify_encrypted_backup(encrypted_path):
                    return False, "Failed to verify encrypted backup"
                
                logger.info(f"Encrypted backup created: {encrypted_path}")
                return True, encrypted_path
                
        except Exception as e:
            logger.error(f"Error creating encrypted backup: {e}")
            return False, str(e)
    
    def _create_database_dump(self, output_path: str, database_name: str = None) -> bool:
        """Create database dump using pg_dump."""
        try:
            # Get database configuration
            db_config = settings.DATABASES['default']
            db_name = database_name or db_config['NAME']
            db_user = db_config['USER']
            db_host = db_config['HOST']
            db_port = db_config['PORT']
            
            # Build pg_dump command
            cmd = [
                'pg_dump',
                '--host', db_host,
                '--port', str(db_port),
                '--username', db_user,
                '--dbname', db_name,
                '--verbose',
                '--no-password',
                '--file', output_path
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config['PASSWORD']:
                env['PGPASSWORD'] = db_config['PASSWORD']
            
            # Execute pg_dump
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"pg_dump failed: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating database dump: {e}")
            return False
    
    def _encrypt_file(self, input_path: str, output_path: str) -> bool:
        """Encrypt file using Fernet encryption."""
        try:
            # Read file content
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted data
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error encrypting file: {e}")
            return False
    
    def _verify_encrypted_backup(self, encrypted_path: str) -> bool:
        """Verify encrypted backup can be decrypted."""
        try:
            # Read encrypted data
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Check if decrypted data is valid
            if len(decrypted_data) > 0:
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error verifying encrypted backup: {e}")
            return False
    
    def restore_encrypted_backup(self, encrypted_path: str, database_name: str = None) -> bool:
        """Restore encrypted backup to database."""
        try:
            # Read encrypted data
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Create temporary file for decrypted data
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
                temp_file.write(decrypted_data)
                temp_path = temp_file.name
            
            try:
                # Restore database
                success = self._restore_database(temp_path, database_name)
                return success
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error restoring encrypted backup: {e}")
            return False
    
    def _restore_database(self, backup_path: str, database_name: str = None) -> bool:
        """Restore database from backup file."""
        try:
            # Get database configuration
            db_config = settings.DATABASES['default']
            db_name = database_name or db_config['NAME']
            db_user = db_config['USER']
            db_host = db_config['HOST']
            db_port = db_config['PORT']
            
            # Build psql command
            cmd = [
                'psql',
                '--host', db_host,
                '--port', str(db_port),
                '--username', db_user,
                '--dbname', db_name,
                '--file', backup_path
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config['PASSWORD']:
                env['PGPASSWORD'] = db_config['PASSWORD']
            
            # Execute psql
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"psql restore failed: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    def list_encrypted_backups(self) -> List[Dict]:
        """List all encrypted backups."""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.enc'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    
                    backup_info = {
                        'filename': filename,
                        'path': file_path,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    }
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
        
        return backups
    
    def cleanup_old_backups(self) -> int:
        """Clean up old backups based on retention policy."""
        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.enc'):
                    file_path = os.path.join(self.backup_dir, filename)
                    stat = os.stat(file_path)
                    file_date = datetime.fromtimestamp(stat.st_ctime)
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        cleaned_count += 1
                        logger.info(f"Cleaned up old backup: {filename}")
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
        
        return cleaned_count
    
    def get_backup_status(self) -> Dict:
        """Get backup status information."""
        backups = self.list_encrypted_backups()
        
        total_size = sum(b['size'] for b in backups)
        oldest_backup = min(backups, key=lambda x: x['created']) if backups else None
        newest_backup = max(backups, key=lambda x: x['created']) if backups else None
        
        return {
            'total_backups': len(backups),
            'total_size': total_size,
            'oldest_backup': oldest_backup['created'] if oldest_backup else None,
            'newest_backup': newest_backup['created'] if newest_backup else None,
            'retention_days': self.retention_days,
            'backup_dir': self.backup_dir
        }


class BackupManagementCommand(BaseCommand):
    """
    Django management command for backup operations.
    """
    
    help = 'Manage encrypted database backups'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create encrypted backup'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List encrypted backups'
        )
        parser.add_argument(
            '--restore',
            type=str,
            help='Restore from encrypted backup (specify filename)'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up old backups'
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show backup status'
        )
    
    def handle(self, *args, **options):
        backup_encryption = BackupEncryption()
        
        if options['create']:
            self.stdout.write('Creating encrypted backup...')
            success, result = backup_encryption.create_encrypted_backup()
            if success:
                self.stdout.write(self.style.SUCCESS(f'Backup created: {result}'))
            else:
                self.stdout.write(self.style.ERROR(f'Backup failed: {result}'))
        
        elif options['list']:
            self.stdout.write('Listing encrypted backups...')
            backups = backup_encryption.list_encrypted_backups()
            for backup in backups:
                self.stdout.write(f'{backup["filename"]} - {backup["size"]} bytes - {backup["created"]}')
        
        elif options['restore']:
            filename = options['restore']
            self.stdout.write(f'Restoring from {filename}...')
            success = backup_encryption.restore_encrypted_backup(filename)
            if success:
                self.stdout.write(self.style.SUCCESS('Backup restored successfully'))
            else:
                self.stdout.write(self.style.ERROR('Backup restore failed'))
        
        elif options['cleanup']:
            self.stdout.write('Cleaning up old backups...')
            cleaned = backup_encryption.cleanup_old_backups()
            self.stdout.write(self.style.SUCCESS(f'Cleaned up {cleaned} old backups'))
        
        elif options['status']:
            self.stdout.write('Backup status:')
            status = backup_encryption.get_backup_status()
            self.stdout.write(f'Total backups: {status["total_backups"]}')
            self.stdout.write(f'Total size: {status["total_size"]} bytes')
            self.stdout.write(f'Retention days: {status["retention_days"]}')
            if status['oldest_backup']:
                self.stdout.write(f'Oldest backup: {status["oldest_backup"]}')
            if status['newest_backup']:
                self.stdout.write(f'Newest backup: {status["newest_backup"]}')
        
        else:
            self.stdout.write(self.style.ERROR('Please specify an action: --create, --list, --restore, --cleanup, or --status'))
