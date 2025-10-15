"""
Add full-text search indexes for improved search performance.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_add_data_validation_constraints'),
    ]

    operations = [
        # Add full-text search index for ticket subject and description
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_fulltext_subject_description 
            ON tickets_ticket USING gin(to_tsvector('english', subject || ' ' || description));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_fulltext_subject_description;"
        ),
        
        # Add full-text search index for ticket comments
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_comments_fulltext_content 
            ON tickets_ticketcomment USING gin(to_tsvector('english', content));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_comments_fulltext_content;"
        ),
        
        # Add full-text search index for canned responses
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_canned_responses_fulltext_name_subject_content 
            ON tickets_cannedresponse USING gin(to_tsvector('english', name || ' ' || subject || ' ' || content));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_canned_responses_fulltext_name_subject_content;"
        ),
        
        # Add full-text search index for user names and emails
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_fulltext_name_email 
            ON accounts_user USING gin(to_tsvector('english', first_name || ' ' || last_name || ' ' || email));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_users_fulltext_name_email;"
        ),
        
        # Add full-text search index for organization names
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_organizations_fulltext_name 
            ON organizations_organization USING gin(to_tsvector('english', name));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_organizations_fulltext_name;"
        ),
        
        # Add full-text search index for department names and descriptions
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_departments_fulltext_name_description 
            ON organizations_department USING gin(to_tsvector('english', name || ' ' || description));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_departments_fulltext_name_description;"
        ),
        
        # Add full-text search index for customer company names
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_fulltext_company 
            ON organizations_customer USING gin(to_tsvector('english', company));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_customers_fulltext_company;"
        ),
        
        # Add full-text search index for ticket history changes
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_history_fulltext_changes 
            ON tickets_tickethistory USING gin(to_tsvector('english', old_value || ' ' || new_value));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_history_fulltext_changes;"
        ),
        
        # Add full-text search index for ticket attachments file names
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ticket_attachments_fulltext_filename 
            ON tickets_ticketattachment USING gin(to_tsvector('english', file_name));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_ticket_attachments_fulltext_filename;"
        ),
        
        # Add full-text search index for user sessions (for security auditing)
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_fulltext_user_agent 
            ON accounts_usersession USING gin(to_tsvector('english', user_agent));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_user_sessions_fulltext_user_agent;"
        ),
        
        # Add full-text search index for user permissions
        migrations.RunSQL(
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_permissions_fulltext_permission 
            ON accounts_userpermission USING gin(to_tsvector('english', permission));
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_user_permissions_fulltext_permission;"
        ),
    ]
