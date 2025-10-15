"""
Add performance indexes for tickets and related models.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        # Add composite indexes for common query patterns
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_org_status_priority ON tickets_ticket (organization_id, status, priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_org_status_priority;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_org_created_status ON tickets_ticket (organization_id, created_at, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_org_created_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_customer_created ON tickets_ticket (customer_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_customer_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_agent_created ON tickets_ticket (assigned_agent_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_agent_created;"
        ),
        
        # Add indexes for ticket comments
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_comments_ticket_created ON tickets_ticketcomment (ticket_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_comments_ticket_created;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_comments_author_created ON tickets_ticketcomment (author_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_comments_author_created;"
        ),
        
        # Add indexes for ticket attachments
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_attachments_ticket ON tickets_ticketattachment (ticket_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_attachments_ticket;"
        ),
        
        # Add partial indexes for active tickets
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_active ON tickets_ticket (organization_id, created_at) WHERE status NOT IN ('closed', 'cancelled');",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_active;"
        ),
        
        # Add indexes for SLA tracking
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_sla_due ON tickets_ticket (organization_id, first_response_due) WHERE first_response_due IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_sla_due;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_resolution_due ON tickets_ticket (organization_id, resolution_due) WHERE resolution_due IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_resolution_due;"
        ),
    ]
