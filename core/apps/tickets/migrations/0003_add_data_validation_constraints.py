"""
Add data validation constraints for improved data integrity.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_add_performance_indexes'),
    ]

    operations = [
        # Add check constraints for data validation
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_satisfaction_score 
            CHECK (customer_satisfaction_score IS NULL OR 
                   (customer_satisfaction_score >= 1 AND customer_satisfaction_score <= 5));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_satisfaction_score;"
        ),
        
        # Add constraint for positive file sizes
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT check_positive_file_size 
            CHECK (file_size > 0);
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS check_positive_file_size;"
        ),
        
        # Add constraint for valid ticket status transitions
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_valid_status 
            CHECK (status IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled'));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_valid_status;"
        ),
        
        # Add constraint for valid priority levels
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_valid_priority 
            CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_valid_priority;"
        ),
        
        # Add constraint for valid user roles
        migrations.RunSQL(
            """
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_role 
            CHECK (role IN ('admin', 'manager', 'agent', 'customer'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_role;"
        ),
        
        # Add constraint for valid customer tiers
        migrations.RunSQL(
            """
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_customer_tier 
            CHECK (customer_tier IN ('basic', 'premium', 'enterprise'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_customer_tier;"
        ),
        
        # Add constraint for positive max concurrent tickets
        migrations.RunSQL(
            """
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_positive_max_tickets 
            CHECK (max_concurrent_tickets > 0);
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_positive_max_tickets;"
        ),
        
        # Add constraint for valid availability status
        migrations.RunSQL(
            """
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_availability_status 
            CHECK (availability_status IN ('available', 'busy', 'away', 'offline'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_availability_status;"
        ),
        
        # Add constraint for valid comment types
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT check_valid_comment_type 
            CHECK (comment_type IN ('public', 'internal', 'system'));
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS check_valid_comment_type;"
        ),
        
        # Add constraint for positive download count
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT check_non_negative_download_count 
            CHECK (download_count >= 0);
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS check_non_negative_download_count;"
        ),
        
        # Add constraint for valid change types
        migrations.RunSQL(
            """
            ALTER TABLE tickets_tickethistory 
            ADD CONSTRAINT check_valid_change_type 
            CHECK (change_type IN ('created', 'updated', 'assigned', 'status_changed', 
                                  'priority_changed', 'resolved', 'closed'));
            """,
            reverse_sql="ALTER TABLE tickets_tickethistory DROP CONSTRAINT IF EXISTS check_valid_change_type;"
        ),
        
        # Add constraint for positive usage count
        migrations.RunSQL(
            """
            ALTER TABLE tickets_cannedresponse 
            ADD CONSTRAINT check_non_negative_usage_count 
            CHECK (usage_count >= 0);
            """,
            reverse_sql="ALTER TABLE tickets_cannedresponse DROP CONSTRAINT IF EXISTS check_non_negative_usage_count;"
        ),
        
        # Add constraint for valid SLA breach boolean
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_sla_breach_boolean 
            CHECK (sla_breach IN (true, false));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_sla_breach_boolean;"
        ),
        
        # Add constraint for valid has_attachments boolean
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT check_has_attachments_boolean 
            CHECK (has_attachments IN (true, false));
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS check_has_attachments_boolean;"
        ),
        
        # Add constraint for valid is_public boolean
        migrations.RunSQL(
            """
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT check_is_public_boolean 
            CHECK (is_public IN (true, false));
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS check_is_public_boolean;"
        ),
        
        # Add constraint for valid is_active boolean
        migrations.RunSQL(
            """
            ALTER TABLE tickets_cannedresponse 
            ADD CONSTRAINT check_is_active_boolean 
            CHECK (is_active IN (true, false));
            """,
            reverse_sql="ALTER TABLE tickets_cannedresponse DROP CONSTRAINT IF EXISTS check_is_active_boolean;"
        ),
    ]
