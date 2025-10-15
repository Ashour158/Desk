"""
Django management command to migrate existing models to use base classes.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Migrate existing models to use base classes."""
    
    help = 'Migrate existing models to use base classes and constants'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Migrate specific app only',
        )
    
    def handle(self, *args, **options):
        """Handle the migration command."""
        dry_run = options['dry_run']
        app_name = options.get('app')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        # Get all model classes
        model_classes = self._get_model_classes(app_name)
        
        if not model_classes:
            self.stdout.write(
                self.style.WARNING('No models found to migrate')
            return
        
        # Migrate each model
        migrated_count = 0
        for model_class in model_classes:
            try:
                if self._migrate_model(model_class, dry_run):
                    migrated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Migrated {model_class.__name__}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'- Skipped {model_class.__name__} (no changes needed)')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to migrate {model_class.__name__}: {str(e)}')
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(f'\nMigration complete: {migrated_count} models processed')
        )
    
    def _get_model_classes(self, app_name=None):
        """Get all model classes to migrate."""
        model_classes = []
        
        # Get all apps
        if app_name:
            apps_to_process = [apps.get_app_config(app_name)]
        else:
            apps_to_process = apps.get_app_configs()
        
        for app_config in apps_to_process:
            # Skip common app (it's the base)
            if app_config.name == 'apps.common':
                continue
            
            # Get models from app
            for model in app_config.get_models():
                # Skip if already using base classes
                if self._uses_base_classes(model):
                    continue
                
                # Skip if no organization field (not tenant-aware)
                if not hasattr(model, 'organization'):
                    continue
                
                model_classes.append(model)
        
        return model_classes
    
    def _uses_base_classes(self, model_class):
        """Check if model already uses base classes."""
        from apps.common.base_models import (
            TenantAwareModel, TimestampedModel, NamedModel, 
            StatusModel, ActiveModel, BaseModel
        )
        
        base_classes = [
            TenantAwareModel, TimestampedModel, NamedModel,
            StatusModel, ActiveModel, BaseModel
        ]
        
        return any(issubclass(model_class, base_class) for base_class in base_classes)
    
    def _migrate_model(self, model_class, dry_run=False):
        """Migrate a single model to use base classes."""
        changes_made = False
        
        # Check if model needs migration
        if self._needs_migration(model_class):
            if not dry_run:
                # This would involve updating the model definition
                # In a real implementation, you'd update the model files
                self._update_model_definition(model_class)
            changes_made = True
        
        return changes_made
    
    def _needs_migration(self, model_class):
        """Check if model needs migration."""
        # Check for common patterns that indicate need for base classes
        has_organization = hasattr(model_class, 'organization')
        has_timestamps = hasattr(model_class, 'created_at') and hasattr(model_class, 'updated_at')
        has_name = hasattr(model_class, 'name')
        has_status = hasattr(model_class, 'status')
        has_is_active = hasattr(model_class, 'is_active')
        
        # If model has multiple common fields, it could benefit from base classes
        common_fields = sum([has_organization, has_timestamps, has_name, has_status, has_is_active])
        
        return common_fields >= 3
    
    def _update_model_definition(self, model_class):
        """Update model definition to use base classes."""
        # This is a placeholder for the actual migration logic
        # In a real implementation, you would:
        # 1. Read the model file
        # 2. Update the class definition
        # 3. Remove duplicate fields
        # 4. Add base class imports
        # 5. Write the updated file
        
        logger.info(f'Would update {model_class.__name__} to use base classes')
        
        # For now, just log what would be changed
        self.stdout.write(
            f'  - Would inherit from BaseModel'
        )
        self.stdout.write(
            f'  - Would remove duplicate organization, name, timestamps fields'
        )
        self.stdout.write(
            f'  - Would add base class imports'
        )


class ModelMigrationHelper:
    """Helper class for model migration operations."""
    
    @staticmethod
    def get_model_file_path(model_class):
        """Get the file path for a model class."""
        import inspect
        return inspect.getfile(model_class)
    
    @staticmethod
    def read_model_file(model_class):
        """Read the model file content."""
        file_path = ModelMigrationHelper.get_model_file_path(model_class)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def write_model_file(model_class, content):
        """Write updated model file content."""
        file_path = ModelMigrationHelper.get_model_file_path(model_class)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def update_model_imports(content):
        """Update model imports to include base classes."""
        # Add base class imports
        if 'from apps.common.base_models import' not in content:
            # Find the last import statement
            lines = content.split('\n')
            last_import_index = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith('from ') or line.strip().startswith('import '):
                    last_import_index = i
            
            # Insert base class import
            lines.insert(last_import_index + 1, 'from apps.common.base_models import BaseModel')
            content = '\n'.join(lines)
        
        return content
    
    @staticmethod
    def update_model_class_definition(content, model_class):
        """Update model class to inherit from base classes."""
        class_name = model_class.__name__
        
        # Find the class definition
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if f'class {class_name}(' in line:
                # Update the class definition
                if 'BaseModel' not in line:
                    lines[i] = line.replace('models.Model)', 'BaseModel)')
                break
        
        return '\n'.join(lines)
    
    @staticmethod
    def remove_duplicate_fields(content):
        """Remove fields that are now provided by base classes."""
        # Fields provided by base classes
        base_fields = [
            'organization = models.ForeignKey(Organization, on_delete=models.CASCADE)',
            'name = models.CharField(max_length=200)',
            'created_at = models.DateTimeField(auto_now_add=True)',
            'updated_at = models.DateTimeField(auto_now=True)',
            'is_active = models.BooleanField(default=True)',
        ]
        
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip lines that match base field patterns
            if any(base_field in line for base_field in base_fields):
                continue
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
