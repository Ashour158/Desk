"""
Add enhanced database constraints to prevent data integrity issues.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database_optimizations', '0001_fix_data_integrity_issues'),
    ]

    operations = [
        # Add comprehensive check constraints for data validation
        migrations.RunSQL(
            """
            -- Add constraint for satisfaction scores
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_satisfaction_score_range 
            CHECK (customer_satisfaction_score IS NULL OR 
                   (customer_satisfaction_score >= 1 AND customer_satisfaction_score <= 5));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_satisfaction_score_range;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for positive file sizes
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT check_positive_file_size 
            CHECK (file_size > 0);
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS check_positive_file_size;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for positive max concurrent tickets
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_positive_max_tickets 
            CHECK (max_concurrent_tickets > 0);
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_positive_max_tickets;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for non-negative usage counts
            ALTER TABLE tickets_cannedresponse 
            ADD CONSTRAINT check_non_negative_usage_count 
            CHECK (usage_count >= 0);
            """,
            reverse_sql="ALTER TABLE tickets_cannedresponse DROP CONSTRAINT IF EXISTS check_non_negative_usage_count;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for non-negative download counts
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT check_non_negative_download_count 
            CHECK (download_count >= 0);
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS check_non_negative_download_count;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid ticket status
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_valid_ticket_status 
            CHECK (status IN ('new', 'open', 'pending', 'resolved', 'closed', 'cancelled'));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_valid_ticket_status;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid ticket priority
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_valid_ticket_priority 
            CHECK (priority IN ('low', 'medium', 'high', 'urgent'));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_valid_ticket_priority;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid ticket channel
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_valid_ticket_channel 
            CHECK (channel IN ('email', 'web', 'phone', 'chat', 'social', 'api'));
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_valid_ticket_channel;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid user role
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_user_role 
            CHECK (role IN ('admin', 'manager', 'agent', 'customer'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_user_role;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid customer tier
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_customer_tier 
            CHECK (customer_tier IN ('basic', 'premium', 'enterprise'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_customer_tier;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid comment type
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT check_valid_comment_type 
            CHECK (comment_type IN ('public', 'internal', 'system'));
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS check_valid_comment_type;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid change type
            ALTER TABLE tickets_tickethistory 
            ADD CONSTRAINT check_valid_change_type 
            CHECK (change_type IN ('created', 'updated', 'assigned', 'status_changed', 'priority_changed', 'resolved', 'closed'));
            """,
            reverse_sql="ALTER TABLE tickets_tickethistory DROP CONSTRAINT IF EXISTS check_valid_change_type;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for valid availability status
            ALTER TABLE accounts_user 
            ADD CONSTRAINT check_valid_availability_status 
            CHECK (availability_status IN ('available', 'busy', 'away', 'offline'));
            """,
            reverse_sql="ALTER TABLE accounts_user DROP CONSTRAINT IF EXISTS check_valid_availability_status;"
        ),
        
        # Add timestamp consistency constraints
        migrations.RunSQL(
            """
            -- Add constraint for timestamp consistency
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_timestamp_consistency 
            CHECK (updated_at >= created_at);
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_timestamp_consistency;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for ticket comment timestamp consistency
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT check_comment_timestamp_consistency 
            CHECK (updated_at >= created_at);
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS check_comment_timestamp_consistency;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for ticket lifecycle consistency
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_ticket_lifecycle_consistency 
            CHECK (
                (resolved_at IS NULL OR resolved_at >= created_at) AND
                (first_response_at IS NULL OR first_response_at >= created_at) AND
                (closed_at IS NULL OR closed_at >= created_at)
            );
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_ticket_lifecycle_consistency;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for session timestamp consistency
            ALTER TABLE accounts_usersession 
            ADD CONSTRAINT check_session_timestamp_consistency 
            CHECK (last_activity >= created_at);
            """,
            reverse_sql="ALTER TABLE accounts_usersession DROP CONSTRAINT IF EXISTS check_session_timestamp_consistency;"
        ),
        
        # Add business logic constraints
        migrations.RunSQL(
            """
            -- Add constraint for customer role validation
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_customer_role 
            CHECK (
                customer_id IS NULL OR 
                customer_id IN (SELECT id FROM accounts_user WHERE role = 'customer')
            );
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_customer_role;"
        ),
        
        migrations.RunSQL(
            """
            -- Add constraint for agent role validation
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT check_agent_role 
            CHECK (
                assigned_agent_id IS NULL OR 
                assigned_agent_id IN (SELECT id FROM accounts_user WHERE role IN ('admin', 'manager', 'agent'))
            );
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS check_agent_role;"
        ),
        
        # Add NOT NULL constraints for critical fields
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for ticket subject
            ALTER TABLE tickets_ticket 
            ALTER COLUMN subject SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticket ALTER COLUMN subject DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for ticket description
            ALTER TABLE tickets_ticket 
            ALTER COLUMN description SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticket ALTER COLUMN description DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for comment content
            ALTER TABLE tickets_ticketcomment 
            ALTER COLUMN content SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment ALTER COLUMN content DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for attachment file name
            ALTER TABLE tickets_ticketattachment 
            ALTER COLUMN file_name SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment ALTER COLUMN file_name DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for attachment file path
            ALTER TABLE tickets_ticketattachment 
            ALTER COLUMN file_path SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment ALTER COLUMN file_path DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for user email
            ALTER TABLE accounts_user 
            ALTER COLUMN email SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE accounts_user ALTER COLUMN email DROP NOT NULL;"
        ),
        
        migrations.RunSQL(
            """
            -- Add NOT NULL constraint for organization name
            ALTER TABLE organizations_organization 
            ALTER COLUMN name SET NOT NULL;
            """,
            reverse_sql="ALTER TABLE organizations_organization ALTER COLUMN name DROP NOT NULL;"
        ),
        
        # Add unique constraints to prevent duplicates
        migrations.RunSQL(
            """
            -- Ensure ticket numbers are unique
            CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_ticket_number_unique 
            ON tickets_ticket (ticket_number);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_ticket_number_unique;"
        ),
        
        migrations.RunSQL(
            """
            -- Ensure session keys are unique
            CREATE UNIQUE INDEX IF NOT EXISTS idx_usersession_session_key_unique 
            ON accounts_usersession (session_key);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_usersession_session_key_unique;"
        ),
        
        migrations.RunSQL(
            """
            -- Ensure organization slugs are unique
            CREATE UNIQUE INDEX IF NOT EXISTS idx_organizations_slug_unique 
            ON organizations_organization (slug);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_organizations_slug_unique;"
        ),
        
        # Add foreign key constraints with proper actions
        migrations.RunSQL(
            """
            -- Add foreign key constraint for ticket-organization relationship
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT fk_ticket_organization 
            FOREIGN KEY (organization_id) REFERENCES organizations_organization(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS fk_ticket_organization;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for ticket-customer relationship
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT fk_ticket_customer 
            FOREIGN KEY (customer_id) REFERENCES accounts_user(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS fk_ticket_customer;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for ticket-agent relationship
            ALTER TABLE tickets_ticket 
            ADD CONSTRAINT fk_ticket_agent 
            FOREIGN KEY (assigned_agent_id) REFERENCES accounts_user(id) 
            ON DELETE SET NULL;
            """,
            reverse_sql="ALTER TABLE tickets_ticket DROP CONSTRAINT IF EXISTS fk_ticket_agent;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for comment-ticket relationship
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT fk_comment_ticket 
            FOREIGN KEY (ticket_id) REFERENCES tickets_ticket(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS fk_comment_ticket;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for comment-author relationship
            ALTER TABLE tickets_ticketcomment 
            ADD CONSTRAINT fk_comment_author 
            FOREIGN KEY (author_id) REFERENCES accounts_user(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticketcomment DROP CONSTRAINT IF EXISTS fk_comment_author;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for attachment-ticket relationship
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT fk_attachment_ticket 
            FOREIGN KEY (ticket_id) REFERENCES tickets_ticket(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS fk_attachment_ticket;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for attachment-comment relationship
            ALTER TABLE tickets_ticketattachment 
            ADD CONSTRAINT fk_attachment_comment 
            FOREIGN KEY (comment_id) REFERENCES tickets_ticketcomment(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE tickets_ticketattachment DROP CONSTRAINT IF EXISTS fk_attachment_comment;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for session-user relationship
            ALTER TABLE accounts_usersession 
            ADD CONSTRAINT fk_session_user 
            FOREIGN KEY (user_id) REFERENCES accounts_user(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE accounts_usersession DROP CONSTRAINT IF EXISTS fk_session_user;"
        ),
        
        migrations.RunSQL(
            """
            -- Add foreign key constraint for permission-user relationship
            ALTER TABLE accounts_userpermission 
            ADD CONSTRAINT fk_permission_user 
            FOREIGN KEY (user_id) REFERENCES accounts_user(id) 
            ON DELETE CASCADE;
            """,
            reverse_sql="ALTER TABLE accounts_userpermission DROP CONSTRAINT IF EXISTS fk_permission_user;"
        ),
    ]
