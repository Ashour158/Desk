"""
Fix critical data integrity issues in the database.
"""

from django.db import migrations, models
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_add_materialized_views'),
    ]

    operations = [
        # Fix orphaned records
        migrations.RunSQL(
            """
            -- Fix orphaned tickets by deleting records with invalid organization references
            DELETE FROM tickets_ticket 
            WHERE organization_id NOT IN (SELECT id FROM organizations_organization);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned ticket comments by deleting records with invalid ticket references
            DELETE FROM tickets_ticketcomment 
            WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned ticket comments by deleting records with invalid author references
            DELETE FROM tickets_ticketcomment 
            WHERE author_id NOT IN (SELECT id FROM accounts_user);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned ticket attachments by deleting records with invalid ticket references
            DELETE FROM tickets_ticketattachment 
            WHERE ticket_id NOT IN (SELECT id FROM tickets_ticket);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned ticket attachments by deleting records with invalid comment references
            DELETE FROM tickets_ticketattachment 
            WHERE comment_id IS NOT NULL 
            AND comment_id NOT IN (SELECT id FROM tickets_ticketcomment);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned user sessions by deleting records with invalid user references
            DELETE FROM accounts_usersession 
            WHERE user_id NOT IN (SELECT id FROM accounts_user);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        migrations.RunSQL(
            """
            -- Fix orphaned user permissions by deleting records with invalid user references
            DELETE FROM accounts_userpermission 
            WHERE user_id NOT IN (SELECT id FROM accounts_user);
            """,
            reverse_sql="-- Cannot reverse orphaned record deletion"
        ),
        
        # Fix duplicate entries
        migrations.RunSQL(
            """
            -- Fix duplicate ticket numbers by keeping the latest record
            DELETE FROM tickets_ticket 
            WHERE id NOT IN (
                SELECT MAX(id) FROM tickets_ticket 
                GROUP BY ticket_number
            );
            """,
            reverse_sql="-- Cannot reverse duplicate removal"
        ),
        
        migrations.RunSQL(
            """
            -- Fix duplicate session keys by keeping the latest record
            DELETE FROM accounts_usersession 
            WHERE id NOT IN (
                SELECT MAX(id) FROM accounts_usersession 
                GROUP BY session_key
            );
            """,
            reverse_sql="-- Cannot reverse duplicate removal"
        ),
        
        migrations.RunSQL(
            """
            -- Fix duplicate user permissions by keeping the latest record
            DELETE FROM accounts_userpermission 
            WHERE id NOT IN (
                SELECT MAX(id) FROM accounts_userpermission 
                GROUP BY user_id, permission
            );
            """,
            reverse_sql="-- Cannot reverse duplicate removal"
        ),
        
        migrations.RunSQL(
            """
            -- Fix duplicate organization slugs by keeping the latest record
            DELETE FROM organizations_organization 
            WHERE id NOT IN (
                SELECT MAX(id) FROM organizations_organization 
                GROUP BY slug
            );
            """,
            reverse_sql="-- Cannot reverse duplicate removal"
        ),
        
        # Fix NULL values
        migrations.RunSQL(
            """
            -- Fix NULL ticket subjects
            UPDATE tickets_ticket 
            SET subject = 'No Subject' 
            WHERE subject IS NULL OR subject = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL ticket descriptions
            UPDATE tickets_ticket 
            SET description = 'No Description' 
            WHERE description IS NULL OR description = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL comment content
            UPDATE tickets_ticketcomment 
            SET content = 'No Content' 
            WHERE content IS NULL OR content = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL attachment file names
            UPDATE tickets_ticketattachment 
            SET file_name = 'unknown_file' 
            WHERE file_name IS NULL OR file_name = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL attachment file paths
            UPDATE tickets_ticketattachment 
            SET file_path = '/unknown/path' 
            WHERE file_path IS NULL OR file_path = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL user emails
            UPDATE accounts_user 
            SET email = CONCAT('user_', id, '@example.com') 
            WHERE email IS NULL OR email = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix NULL organization names
            UPDATE organizations_organization 
            SET name = CONCAT('Organization ', id) 
            WHERE name IS NULL OR name = '';
            """,
            reverse_sql="-- Cannot reverse NULL value fixes"
        ),
        
        # Fix invalid enum values
        migrations.RunSQL(
            """
            -- Fix invalid ticket status values
            UPDATE tickets_ticket 
            SET status = 'new' 
            WHERE status NOT IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid ticket priority values
            UPDATE tickets_ticket 
            SET priority = 'medium' 
            WHERE priority NOT IN ('low', 'medium', 'high', 'urgent');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid ticket channel values
            UPDATE tickets_ticket 
            SET channel = 'web' 
            WHERE channel NOT IN ('email', 'web', 'phone', 'chat', 'social', 'api');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid user role values
            UPDATE accounts_user 
            SET role = 'customer' 
            WHERE role NOT IN ('admin', 'manager', 'agent', 'customer');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid customer tier values
            UPDATE accounts_user 
            SET customer_tier = 'basic' 
            WHERE customer_tier NOT IN ('basic', 'premium', 'enterprise');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid comment type values
            UPDATE tickets_ticketcomment 
            SET comment_type = 'public' 
            WHERE comment_type NOT IN ('public', 'internal', 'system');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid change type values
            UPDATE tickets_tickethistory 
            SET change_type = 'updated' 
            WHERE change_type NOT IN ('created', 'updated', 'assigned', 'status_changed', 'priority_changed', 'resolved', 'closed');
            """,
            reverse_sql="-- Cannot reverse enum value fixes"
        ),
        
        # Fix timestamp inconsistencies
        migrations.RunSQL(
            """
            -- Fix tickets where updated_at is before created_at
            UPDATE tickets_ticket 
            SET updated_at = created_at 
            WHERE updated_at < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix ticket comments where updated_at is before created_at
            UPDATE tickets_ticketcomment 
            SET updated_at = created_at 
            WHERE updated_at < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix tickets where resolved_at is before created_at
            UPDATE tickets_ticket 
            SET resolved_at = created_at + INTERVAL '1 hour' 
            WHERE resolved_at IS NOT NULL AND resolved_at < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix tickets where first_response_at is before created_at
            UPDATE tickets_ticket 
            SET first_response_at = created_at + INTERVAL '30 minutes' 
            WHERE first_response_at IS NOT NULL AND first_response_at < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix tickets where closed_at is before created_at
            UPDATE tickets_ticket 
            SET closed_at = created_at + INTERVAL '2 hours' 
            WHERE closed_at IS NOT NULL AND closed_at < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix user sessions where last_activity is before created_at
            UPDATE accounts_usersession 
            SET last_activity = created_at 
            WHERE last_activity < created_at;
            """,
            reverse_sql="-- Cannot reverse timestamp fixes"
        ),
        
        # Fix data inconsistencies
        migrations.RunSQL(
            """
            -- Fix invalid satisfaction scores
            UPDATE tickets_ticket 
            SET customer_satisfaction_score = 3 
            WHERE customer_satisfaction_score IS NOT NULL 
            AND (customer_satisfaction_score < 1 OR customer_satisfaction_score > 5);
            """,
            reverse_sql="-- Cannot reverse data inconsistency fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid file sizes
            UPDATE tickets_ticketattachment 
            SET file_size = 1024 
            WHERE file_size <= 0;
            """,
            reverse_sql="-- Cannot reverse data inconsistency fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid max concurrent tickets
            UPDATE accounts_user 
            SET max_concurrent_tickets = 10 
            WHERE max_concurrent_tickets <= 0;
            """,
            reverse_sql="-- Cannot reverse data inconsistency fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid usage counts
            UPDATE tickets_cannedresponse 
            SET usage_count = 0 
            WHERE usage_count < 0;
            """,
            reverse_sql="-- Cannot reverse data inconsistency fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix invalid download counts
            UPDATE tickets_ticketattachment 
            SET download_count = 0 
            WHERE download_count < 0;
            """,
            reverse_sql="-- Cannot reverse data inconsistency fixes"
        ),
        
        # Fix referential integrity issues
        migrations.RunSQL(
            """
            -- Fix tickets where customer is not actually a customer
            UPDATE tickets_ticket 
            SET customer_id = (
                SELECT id FROM accounts_user 
                WHERE role = 'customer' 
                LIMIT 1
            )
            WHERE customer_id IN (
                SELECT id FROM accounts_user 
                WHERE role != 'customer'
            );
            """,
            reverse_sql="-- Cannot reverse referential integrity fixes"
        ),
        
        migrations.RunSQL(
            """
            -- Fix tickets where assigned_agent is not actually an agent
            UPDATE tickets_ticket 
            SET assigned_agent_id = NULL 
            WHERE assigned_agent_id IN (
                SELECT id FROM accounts_user 
                WHERE role NOT IN ('admin', 'manager', 'agent')
            );
            """,
            reverse_sql="-- Cannot reverse referential integrity fixes"
        ),
        
        # Update SLA breach flags
        migrations.RunSQL(
            """
            -- Update SLA breach flags for first response
            UPDATE tickets_ticket 
            SET sla_breach = true 
            WHERE first_response_at IS NOT NULL 
            AND first_response_due IS NOT NULL 
            AND first_response_at > first_response_due;
            """,
            reverse_sql="-- Cannot reverse SLA breach updates"
        ),
        
        migrations.RunSQL(
            """
            -- Update SLA breach flags for resolution
            UPDATE tickets_ticket 
            SET sla_breach = true 
            WHERE resolved_at IS NOT NULL 
            AND resolution_due IS NOT NULL 
            AND resolved_at > resolution_due;
            """,
            reverse_sql="-- Cannot reverse SLA breach updates"
        ),
    ]
