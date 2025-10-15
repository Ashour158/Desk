"""
Management command to setup automated backup strategy.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from datetime import datetime, timedelta
from pathlib import Path


class Command(BaseCommand):
    """Setup automated backup strategy command."""
    
    help = 'Setup automated backup strategy with scheduling and monitoring'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--backup-type',
            choices=['database', 'files', 'full'],
            default='full',
            help='Type of backup to setup (default: full)',
        )
        parser.add_argument(
            '--retention-days',
            type=int,
            default=30,
            help='Number of days to retain backups (default: 30)',
        )
        parser.add_argument(
            '--backup-location',
            type=str,
            default='/backups',
            help='Location to store backups (default: /backups)',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        backup_type = options['backup_type']
        retention_days = options['retention_days']
        backup_location = options['backup_location']
        
        self.stdout.write(
            self.style.SUCCESS(f"Setting up {backup_type} backup strategy...")
        )
        
        # Create backup directory
        backup_path = Path(backup_location)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create backup scripts
        self._create_database_backup_script(backup_path, retention_days)
        self._create_files_backup_script(backup_path, retention_days)
        self._create_full_backup_script(backup_path, retention_days)
        self._create_backup_monitoring_script(backup_path)
        self._create_cron_jobs(backup_type, backup_path)
        self._create_backup_configuration(backup_path, retention_days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Backup strategy setup complete!\n"
                f"- Backup location: {backup_path}\n"
                f"- Retention: {retention_days} days\n"
                f"- Type: {backup_type}"
            )
        )
    
    def _create_database_backup_script(self, backup_path, retention_days):
        """Create database backup script."""
        script_content = f'''#!/bin/bash
# Database backup script
# Generated on {datetime.now().isoformat()}

set -e

# Configuration
BACKUP_DIR="{backup_path}/database"
RETENTION_DAYS={retention_days}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="${{DB_NAME:-helpdesk_production}}"
DB_USER="${{DB_USER:-helpdesk_user}}"
DB_HOST="${{DB_HOST:-localhost}}"
DB_PORT="${{DB_PORT:-5432}}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create database backup
echo "Creating database backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \\
    --verbose --no-password --format=custom \\
    --file="$BACKUP_DIR/backup_$TIMESTAMP.dump"

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_DIR/backup_$TIMESTAMP.dump"

# Clean up old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "backup_*.dump.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup
if [ -f "$BACKUP_DIR/backup_$TIMESTAMP.dump.gz" ]; then
    echo "Database backup completed successfully: backup_$TIMESTAMP.dump.gz"
    exit 0
else
    echo "Database backup failed!"
    exit 1
fi
'''
        
        script_path = backup_path / 'backup_database.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        self.stdout.write(f"Created database backup script: {script_path}")
    
    def _create_files_backup_script(self, backup_path, retention_days):
        """Create files backup script."""
        script_content = f'''#!/bin/bash
# Files backup script
# Generated on {datetime.now().isoformat()}

set -e

# Configuration
BACKUP_DIR="{backup_path}/files"
RETENTION_DAYS={retention_days}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SOURCE_DIRS=(
    "media"
    "staticfiles"
    "logs"
    "config"
)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create files backup
echo "Creating files backup..."
tar -czf "$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz" "${{SOURCE_DIRS[@]}}"

# Clean up old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "files_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup
if [ -f "$BACKUP_DIR/files_backup_$TIMESTAMP.tar.gz" ]; then
    echo "Files backup completed successfully: files_backup_$TIMESTAMP.tar.gz"
    exit 0
else
    echo "Files backup failed!"
    exit 1
fi
'''
        
        script_path = backup_path / 'backup_files.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        self.stdout.write(f"Created files backup script: {script_path}")
    
    def _create_full_backup_script(self, backup_path, retention_days):
        """Create full backup script."""
        script_content = f'''#!/bin/bash
# Full backup script
# Generated on {datetime.now().isoformat()}

set -e

# Configuration
BACKUP_DIR="{backup_path}/full"
RETENTION_DAYS={retention_days}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Run database backup
echo "Running database backup..."
{backup_path}/backup_database.sh

# Run files backup
echo "Running files backup..."
{backup_path}/backup_files.sh

# Create full backup archive
echo "Creating full backup archive..."
tar -czf "$BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz" \\
    "${{BACKUP_DIR}}/database/backup_$TIMESTAMP.dump.gz" \\
    "${{BACKUP_DIR}}/files/files_backup_$TIMESTAMP.tar.gz"

# Clean up individual backups
rm -f "${{BACKUP_DIR}}/database/backup_$TIMESTAMP.dump.gz"
rm -f "${{BACKUP_DIR}}/files/files_backup_$TIMESTAMP.tar.gz"

# Clean up old full backups
echo "Cleaning up old full backups..."
find "$BACKUP_DIR" -name "full_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup
if [ -f "$BACKUP_DIR/full_backup_$TIMESTAMP.tar.gz" ]; then
    echo "Full backup completed successfully: full_backup_$TIMESTAMP.tar.gz"
    exit 0
else
    echo "Full backup failed!"
    exit 1
fi
'''
        
        script_path = backup_path / 'backup_full.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        self.stdout.write(f"Created full backup script: {script_path}")
    
    def _create_backup_monitoring_script(self, backup_path):
        """Create backup monitoring script."""
        script_content = f'''#!/bin/bash
# Backup monitoring script
# Generated on {datetime.now().isoformat()}

set -e

# Configuration
BACKUP_DIR="{backup_path}"
LOG_FILE="$BACKUP_DIR/backup_monitor.log"
ALERT_EMAIL="${{ALERT_EMAIL:-admin@helpdesk.com}}"

# Function to log messages
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}}

# Function to send alert
send_alert() {{
    local subject="$1"
    local message="$2"
    
    echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
    log_message "ALERT: $subject - $message"
}}

# Check backup status
check_backup_status() {{
    local backup_type="$1"
    local max_age_hours="$2"
    
    case "$backup_type" in
        "database")
            latest_backup=$(find "$BACKUP_DIR/database" -name "backup_*.dump.gz" -type f -printf '%T@ %p\\n' | sort -n | tail -1 | cut -d' ' -f2)
            ;;
        "files")
            latest_backup=$(find "$BACKUP_DIR/files" -name "files_backup_*.tar.gz" -type f -printf '%T@ %p\\n' | sort -n | tail -1 | cut -d' ' -f2)
            ;;
        "full")
            latest_backup=$(find "$BACKUP_DIR/full" -name "full_backup_*.tar.gz" -type f -printf '%T@ %p\\n' | sort -n | tail -1 | cut -d' ' -f2)
            ;;
    esac
    
    if [ -z "$latest_backup" ]; then
        send_alert "Backup Alert: No $backup_type backup found" "No $backup_type backup found in $BACKUP_DIR"
        return 1
    fi
    
    # Check backup age
    backup_age=$(($(date +%s) - $(stat -c %Y "$latest_backup")))
    max_age_seconds=$((max_age_hours * 3600))
    
    if [ $backup_age -gt $max_age_seconds ]; then
        send_alert "Backup Alert: $backup_type backup is too old" "Latest $backup_type backup is $((backup_age / 3600)) hours old (max: $max_age_hours hours)"
        return 1
    fi
    
    # Check backup size
    backup_size=$(stat -c %s "$latest_backup")
    if [ $backup_size -lt 1024 ]; then  # Less than 1KB
        send_alert "Backup Alert: $backup_type backup is too small" "Latest $backup_type backup is only $backup_size bytes"
        return 1
    fi
    
    log_message "Backup check passed: $backup_type backup is healthy"
    return 0
}}

# Main monitoring logic
log_message "Starting backup monitoring..."

# Check database backups (max 25 hours old)
check_backup_status "database" 25

# Check files backups (max 25 hours old)
check_backup_status "files" 25

# Check full backups (max 25 hours old)
check_backup_status "full" 25

log_message "Backup monitoring completed"
'''
        
        script_path = backup_path / 'monitor_backups.sh'
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        self.stdout.write(f"Created backup monitoring script: {script_path}")
    
    def _create_cron_jobs(self, backup_type, backup_path):
        """Create cron jobs for automated backups."""
        cron_content = f'''# Automated backup cron jobs
# Generated on {datetime.now().isoformat()}

# Database backup - daily at 2 AM
0 2 * * * {backup_path}/backup_database.sh >> {backup_path}/backup_database.log 2>&1

# Files backup - daily at 3 AM
0 3 * * * {backup_path}/backup_files.sh >> {backup_path}/backup_files.log 2>&1

# Full backup - weekly on Sunday at 1 AM
0 1 * * 0 {backup_path}/backup_full.sh >> {backup_path}/backup_full.log 2>&1

# Backup monitoring - every 6 hours
0 */6 * * * {backup_path}/monitor_backups.sh >> {backup_path}/backup_monitor.log 2>&1

# Cleanup old logs - weekly on Monday at 4 AM
0 4 * * 1 find {backup_path} -name "*.log" -mtime +7 -delete
'''
        
        cron_path = backup_path / 'backup_cron.txt'
        with open(cron_path, 'w') as f:
            f.write(cron_content)
        
        self.stdout.write(f"Created cron jobs file: {cron_path}")
        self.stdout.write(
            self.style.WARNING(
                f"To activate cron jobs, run: crontab {cron_path}"
            )
        )
    
    def _create_backup_configuration(self, backup_path, retention_days):
        """Create backup configuration file."""
        config = {
            'backup_strategy': {
                'database': {
                    'enabled': True,
                    'schedule': '0 2 * * *',  # Daily at 2 AM
                    'retention_days': retention_days,
                    'compression': True,
                    'encryption': False,
                },
                'files': {
                    'enabled': True,
                    'schedule': '0 3 * * *',  # Daily at 3 AM
                    'retention_days': retention_days,
                    'include_dirs': ['media', 'staticfiles', 'logs', 'config'],
                    'exclude_patterns': ['*.tmp', '*.log'],
                },
                'full': {
                    'enabled': True,
                    'schedule': '0 1 * * 0',  # Weekly on Sunday at 1 AM
                    'retention_days': retention_days,
                    'includes': ['database', 'files'],
                }
            },
            'monitoring': {
                'enabled': True,
                'check_interval': '0 */6 * * *',  # Every 6 hours
                'alert_email': 'admin@helpdesk.com',
                'max_backup_age_hours': 25,
                'min_backup_size_bytes': 1024,
            },
            'storage': {
                'local_path': str(backup_path),
                'cloud_sync': False,
                'encryption_key': None,
            },
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        config_path = backup_path / 'backup_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.stdout.write(f"Created backup configuration: {config_path}")
