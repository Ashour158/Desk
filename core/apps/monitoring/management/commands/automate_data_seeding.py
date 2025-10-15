"""
Management command to automate data seeding processes.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Automate data seeding command."""
    
    help = 'Automate data seeding processes with monitoring and validation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--seed-type',
            choices=['basic', 'comprehensive', 'test', 'production'],
            default='basic',
            help='Type of data seeding to perform (default: basic)',
        )
        parser.add_argument(
            '--validate-data',
            action='store_true',
            help='Validate seeded data for integrity',
        )
        parser.add_argument(
            '--monitor-performance',
            action='store_true',
            help='Monitor seeding performance',
        )
        parser.add_argument(
            '--output-report',
            type=str,
            default='seeding_report.json',
            help='Output file for seeding report',
        )
        parser.add_argument(
            '--cleanup-before',
            action='store_true',
            help='Clean up existing data before seeding',
        )
    
    def handle(self, *args, **options):
        """Handle the command."""
        seed_type = options['seed_type']
        validate_data = options['validate_data']
        monitor_performance = options['monitor_performance']
        output_report = options['output_report']
        cleanup_before = options['cleanup_before']
        
        self.stdout.write(
            self.style.SUCCESS(f"Starting {seed_type} data seeding...")
        )
        
        # Initialize seeding report
        seeding_report = {
            'start_time': timezone.now().isoformat(),
            'seed_type': seed_type,
            'options': options,
            'steps': [],
            'performance_metrics': {},
            'validation_results': {},
            'errors': [],
            'summary': {}
        }
        
        try:
            # Cleanup before seeding if requested
            if cleanup_before:
                self._cleanup_existing_data(seeding_report)
            
            # Perform seeding based on type
            if seed_type == 'basic':
                self._seed_basic_data(seeding_report, monitor_performance)
            elif seed_type == 'comprehensive':
                self._seed_comprehensive_data(seeding_report, monitor_performance)
            elif seed_type == 'test':
                self._seed_test_data(seeding_report, monitor_performance)
            elif seed_type == 'production':
                self._seed_production_data(seeding_report, monitor_performance)
            
            # Validate data if requested
            if validate_data:
                self._validate_seeded_data(seeding_report)
            
            # Generate summary
            self._generate_seeding_summary(seeding_report)
            
            # Save report
            self._save_seeding_report(seeding_report, output_report)
            
            # Display results
            self._display_seeding_results(seeding_report)
            
            self.stdout.write(
                self.style.SUCCESS("Data seeding completed successfully!")
            )
            
        except Exception as e:
            seeding_report['errors'].append(str(e))
            self.stdout.write(
                self.style.ERROR(f"Data seeding failed: {e}")
            )
            raise
    
    def _cleanup_existing_data(self, report):
        """Clean up existing data before seeding."""
        self.stdout.write("Cleaning up existing data...")
        
        start_time = timezone.now()
        
        try:
            # Clean up in reverse dependency order
            cleanup_steps = [
                ('User Sessions', 'DELETE FROM django_session;'),
                ('User Permissions', 'DELETE FROM auth_user_groups; DELETE FROM auth_user_user_permissions;'),
                ('User Profiles', 'DELETE FROM accounts_userprofile;'),
                ('Tickets', 'DELETE FROM tickets_ticket;'),
                ('Organizations', 'DELETE FROM organizations_organization;'),
                ('Users', 'DELETE FROM auth_user WHERE is_superuser = FALSE;'),
            ]
            
            with transaction.atomic():
                for step_name, sql in cleanup_steps:
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                        affected_rows = cursor.rowcount
                    
                    report['steps'].append({
                        'step': f'Cleanup {step_name}',
                        'status': 'success',
                        'affected_rows': affected_rows,
                        'timestamp': timezone.now().isoformat()
                    })
            
            duration = (timezone.now() - start_time).total_seconds()
            report['performance_metrics']['cleanup_duration'] = duration
            
            self.stdout.write(f"✓ Cleanup completed in {duration:.2f}s")
            
        except Exception as e:
            report['steps'].append({
                'step': 'Cleanup',
                'status': 'failed',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            })
            raise
    
    def _seed_basic_data(self, report, monitor_performance):
        """Seed basic data for system operation."""
        self.stdout.write("Seeding basic data...")
        
        start_time = timezone.now()
        
        try:
            with transaction.atomic():
                # Create organizations
                organizations = self._create_organizations(report)
                
                # Create users
                users = self._create_users(report, organizations)
                
                # Create basic tickets
                tickets = self._create_basic_tickets(report, users)
                
                # Create system settings
                settings = self._create_system_settings(report)
            
            duration = (timezone.now() - start_time).total_seconds()
            report['performance_metrics']['seeding_duration'] = duration
            
            report['summary'].update({
                'organizations_created': len(organizations),
                'users_created': len(users),
                'tickets_created': len(tickets),
                'settings_created': len(settings),
            })
            
            self.stdout.write(f"✓ Basic data seeded in {duration:.2f}s")
            
        except Exception as e:
            report['errors'].append(f"Basic data seeding failed: {e}")
            raise
    
    def _seed_comprehensive_data(self, report, monitor_performance):
        """Seed comprehensive data for full system testing."""
        self.stdout.write("Seeding comprehensive data...")
        
        start_time = timezone.now()
        
        try:
            with transaction.atomic():
                # Create organizations with full data
                organizations = self._create_organizations(report, comprehensive=True)
                
                # Create users with profiles
                users = self._create_users(report, organizations, comprehensive=True)
                
                # Create tickets with full workflow
                tickets = self._create_comprehensive_tickets(report, users)
                
                # Create knowledge base
                kb_articles = self._create_knowledge_base(report)
                
                # Create workflows
                workflows = self._create_workflows(report)
                
                # Create integrations
                integrations = self._create_integrations(report)
            
            duration = (timezone.now() - start_time).total_seconds()
            report['performance_metrics']['seeding_duration'] = duration
            
            report['summary'].update({
                'organizations_created': len(organizations),
                'users_created': len(users),
                'tickets_created': len(tickets),
                'kb_articles_created': len(kb_articles),
                'workflows_created': len(workflows),
                'integrations_created': len(integrations),
            })
            
            self.stdout.write(f"✓ Comprehensive data seeded in {duration:.2f}s")
            
        except Exception as e:
            report['errors'].append(f"Comprehensive data seeding failed: {e}")
            raise
    
    def _seed_test_data(self, report, monitor_performance):
        """Seed test data for development and testing."""
        self.stdout.write("Seeding test data...")
        
        start_time = timezone.now()
        
        try:
            with transaction.atomic():
                # Create test organizations
                test_orgs = self._create_test_organizations(report)
                
                # Create test users
                test_users = self._create_test_users(report, test_orgs)
                
                # Create test tickets
                test_tickets = self._create_test_tickets(report, test_users)
                
                # Create test data for all modules
                test_data = self._create_test_module_data(report)
            
            duration = (timezone.now() - start_time).total_seconds()
            report['performance_metrics']['seeding_duration'] = duration
            
            report['summary'].update({
                'test_organizations': len(test_orgs),
                'test_users': len(test_users),
                'test_tickets': len(test_tickets),
                'test_data_entries': len(test_data),
            })
            
            self.stdout.write(f"✓ Test data seeded in {duration:.2f}s")
            
        except Exception as e:
            report['errors'].append(f"Test data seeding failed: {e}")
            raise
    
    def _seed_production_data(self, report, monitor_performance):
        """Seed production data with real-world scenarios."""
        self.stdout.write("Seeding production data...")
        
        start_time = timezone.now()
        
        try:
            with transaction.atomic():
                # Create production organizations
                prod_orgs = self._create_production_organizations(report)
                
                # Create production users
                prod_users = self._create_production_users(report, prod_orgs)
                
                # Create production tickets
                prod_tickets = self._create_production_tickets(report, prod_users)
                
                # Create production configurations
                prod_configs = self._create_production_configurations(report)
            
            duration = (timezone.now() - start_time).total_seconds()
            report['performance_metrics']['seeding_duration'] = duration
            
            report['summary'].update({
                'production_organizations': len(prod_orgs),
                'production_users': len(prod_users),
                'production_tickets': len(prod_tickets),
                'production_configurations': len(prod_configs),
            })
            
            self.stdout.write(f"✓ Production data seeded in {duration:.2f}s")
            
        except Exception as e:
            report['errors'].append(f"Production data seeding failed: {e}")
            raise
    
    def _create_organizations(self, report, comprehensive=False):
        """Create organizations."""
        organizations = []
        
        org_data = [
            {'name': 'Acme Corp', 'domain': 'acme.com', 'type': 'enterprise'},
            {'name': 'TechStart Inc', 'domain': 'techstart.com', 'type': 'startup'},
            {'name': 'Global Solutions', 'domain': 'globalsolutions.com', 'type': 'enterprise'},
        ]
        
        if comprehensive:
            org_data.extend([
                {'name': 'Small Business Co', 'domain': 'smallbiz.com', 'type': 'small_business'},
                {'name': 'Enterprise Ltd', 'domain': 'enterprise.com', 'type': 'enterprise'},
                {'name': 'Non-Profit Org', 'domain': 'nonprofit.org', 'type': 'non_profit'},
            ])
        
        for org_info in org_data:
            try:
                # Create organization using Django ORM
                from apps.organizations.models import Organization
                
                org = Organization.objects.create(
                    name=org_info['name'],
                    domain=org_info['domain'],
                    organization_type=org_info['type'],
                    created_at=timezone.now()
                )
                
                organizations.append(org)
                
                report['steps'].append({
                    'step': f'Create organization: {org_info["name"]}',
                    'status': 'success',
                    'timestamp': timezone.now().isoformat()
                })
                
            except Exception as e:
                report['steps'].append({
                    'step': f'Create organization: {org_info["name"]}',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
        
        return organizations
    
    def _create_users(self, report, organizations, comprehensive=False):
        """Create users."""
        users = []
        
        user_data = [
            {'username': 'admin', 'email': 'admin@helpdesk.com', 'role': 'admin'},
            {'username': 'manager1', 'email': 'manager1@acme.com', 'role': 'manager'},
            {'username': 'agent1', 'email': 'agent1@acme.com', 'role': 'agent'},
            {'username': 'customer1', 'email': 'customer1@acme.com', 'role': 'customer'},
        ]
        
        if comprehensive:
            user_data.extend([
                {'username': 'manager2', 'email': 'manager2@techstart.com', 'role': 'manager'},
                {'username': 'agent2', 'email': 'agent2@techstart.com', 'role': 'agent'},
                {'username': 'customer2', 'email': 'customer2@techstart.com', 'role': 'customer'},
                {'username': 'customer3', 'email': 'customer3@globalsolutions.com', 'role': 'customer'},
            ])
        
        for user_info in user_data:
            try:
                user = User.objects.create_user(
                    username=user_info['username'],
                    email=user_info['email'],
                    password='testpass123',
                    first_name=user_info['username'].title(),
                    last_name='User',
                    is_staff=user_info['role'] in ['admin', 'manager', 'agent'],
                    is_superuser=user_info['role'] == 'admin'
                )
                
                # Assign to organization
                if organizations:
                    user.organization = organizations[0]
                    user.save()
                
                users.append(user)
                
                report['steps'].append({
                    'step': f'Create user: {user_info["username"]}',
                    'status': 'success',
                    'timestamp': timezone.now().isoformat()
                })
                
            except Exception as e:
                report['steps'].append({
                    'step': f'Create user: {user_info["username"]}',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
        
        return users
    
    def _create_basic_tickets(self, report, users):
        """Create basic tickets."""
        tickets = []
        
        ticket_data = [
            {'subject': 'Login Issue', 'description': 'Cannot login to the system', 'priority': 'high'},
            {'subject': 'Password Reset', 'description': 'Need to reset password', 'priority': 'medium'},
            {'subject': 'Feature Request', 'description': 'Add new feature', 'priority': 'low'},
        ]
        
        for ticket_info in ticket_data:
            try:
                from apps.tickets.models import Ticket
                
                ticket = Ticket.objects.create(
                    subject=ticket_info['subject'],
                    description=ticket_info['description'],
                    priority=ticket_info['priority'],
                    status='new',
                    customer=users[0] if users else None,
                    created_by=users[0] if users else None,
                    created_at=timezone.now()
                )
                
                tickets.append(ticket)
                
                report['steps'].append({
                    'step': f'Create ticket: {ticket_info["subject"]}',
                    'status': 'success',
                    'timestamp': timezone.now().isoformat()
                })
                
            except Exception as e:
                report['steps'].append({
                    'step': f'Create ticket: {ticket_info["subject"]}',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                })
        
        return tickets
    
    def _create_comprehensive_tickets(self, report, users):
        """Create comprehensive tickets with full workflow."""
        # Implementation for comprehensive ticket creation
        return []
    
    def _create_knowledge_base(self, report):
        """Create knowledge base articles."""
        # Implementation for knowledge base creation
        return []
    
    def _create_workflows(self, report):
        """Create workflows."""
        # Implementation for workflow creation
        return []
    
    def _create_integrations(self, report):
        """Create integrations."""
        # Implementation for integration creation
        return []
    
    def _create_test_organizations(self, report):
        """Create test organizations."""
        # Implementation for test organization creation
        return []
    
    def _create_test_users(self, report, organizations):
        """Create test users."""
        # Implementation for test user creation
        return []
    
    def _create_test_tickets(self, report, users):
        """Create test tickets."""
        # Implementation for test ticket creation
        return []
    
    def _create_test_module_data(self, report):
        """Create test data for all modules."""
        # Implementation for test module data creation
        return []
    
    def _create_production_organizations(self, report):
        """Create production organizations."""
        # Implementation for production organization creation
        return []
    
    def _create_production_users(self, report, organizations):
        """Create production users."""
        # Implementation for production user creation
        return []
    
    def _create_production_tickets(self, report, users):
        """Create production tickets."""
        # Implementation for production ticket creation
        return []
    
    def _create_production_configurations(self, report):
        """Create production configurations."""
        # Implementation for production configuration creation
        return []
    
    def _create_system_settings(self, report):
        """Create system settings."""
        # Implementation for system settings creation
        return []
    
    def _validate_seeded_data(self, report):
        """Validate seeded data for integrity."""
        self.stdout.write("Validating seeded data...")
        
        validation_results = {
            'organizations': self._validate_organizations(),
            'users': self._validate_users(),
            'tickets': self._validate_tickets(),
            'relationships': self._validate_relationships(),
        }
        
        report['validation_results'] = validation_results
        
        # Check for validation errors
        errors = []
        for category, results in validation_results.items():
            if not results['valid']:
                errors.extend(results['errors'])
        
        if errors:
            report['errors'].extend(errors)
            self.stdout.write(
                self.style.WARNING(f"Validation found {len(errors)} issues")
            )
        else:
            self.stdout.write("✓ Data validation passed")
    
    def _validate_organizations(self):
        """Validate organizations."""
        try:
            from apps.organizations.models import Organization
            
            orgs = Organization.objects.all()
            
            if not orgs.exists():
                return {'valid': False, 'errors': ['No organizations found']}
            
            errors = []
            for org in orgs:
                if not org.name:
                    errors.append(f'Organization {org.id} has no name')
                if not org.domain:
                    errors.append(f'Organization {org.id} has no domain')
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def _validate_users(self):
        """Validate users."""
        try:
            users = User.objects.all()
            
            if not users.exists():
                return {'valid': False, 'errors': ['No users found']}
            
            errors = []
            for user in users:
                if not user.email:
                    errors.append(f'User {user.id} has no email')
                if not user.username:
                    errors.append(f'User {user.id} has no username')
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def _validate_tickets(self):
        """Validate tickets."""
        try:
            from apps.tickets.models import Ticket
            
            tickets = Ticket.objects.all()
            
            if not tickets.exists():
                return {'valid': False, 'errors': ['No tickets found']}
            
            errors = []
            for ticket in tickets:
                if not ticket.subject:
                    errors.append(f'Ticket {ticket.id} has no subject')
                if not ticket.description:
                    errors.append(f'Ticket {ticket.id} has no description')
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def _validate_relationships(self):
        """Validate data relationships."""
        try:
            errors = []
            
            # Check user-organization relationships
            from apps.organizations.models import Organization
            users_without_orgs = User.objects.filter(organization__isnull=True).count()
            if users_without_orgs > 0:
                errors.append(f'{users_without_orgs} users have no organization')
            
            # Check ticket-user relationships
            from apps.tickets.models import Ticket
            tickets_without_customers = Ticket.objects.filter(customer__isnull=True).count()
            if tickets_without_customers > 0:
                errors.append(f'{tickets_without_customers} tickets have no customer')
            
            return {'valid': len(errors) == 0, 'errors': errors}
            
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    def _generate_seeding_summary(self, report):
        """Generate seeding summary."""
        report['summary'].update({
            'total_steps': len(report['steps']),
            'successful_steps': len([s for s in report['steps'] if s['status'] == 'success']),
            'failed_steps': len([s for s in report['steps'] if s['status'] == 'failed']),
            'total_errors': len(report['errors']),
            'end_time': timezone.now().isoformat(),
        })
    
    def _save_seeding_report(self, report, output_file):
        """Save seeding report to file."""
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def _display_seeding_results(self, report):
        """Display seeding results."""
        summary = report['summary']
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("DATA SEEDING RESULTS")
        self.stdout.write("="*60)
        
        self.stdout.write(f"\nSeeding Type: {report['seed_type']}")
        self.stdout.write(f"Total Steps: {summary['total_steps']}")
        self.stdout.write(f"Successful: {summary['successful_steps']}")
        self.stdout.write(f"Failed: {summary['failed_steps']}")
        self.stdout.write(f"Errors: {summary['total_errors']}")
        
        if 'seeding_duration' in report['performance_metrics']:
            duration = report['performance_metrics']['seeding_duration']
            self.stdout.write(f"Duration: {duration:.2f}s")
        
        # Display created data summary
        for key, value in summary.items():
            if key.endswith('_created') and value > 0:
                self.stdout.write(f"{key.replace('_', ' ').title()}: {value}")
        
        # Display validation results
        if report['validation_results']:
            self.stdout.write("\nValidation Results:")
            for category, results in report['validation_results'].items():
                status = "✓" if results['valid'] else "✗"
                self.stdout.write(f"{status} {category.title()}: {len(results['errors'])} errors")
        
        # Display errors if any
        if report['errors']:
            self.stdout.write("\nErrors:")
            for error in report['errors']:
                self.stdout.write(f"- {error}")
        
        self.stdout.write("="*60)
