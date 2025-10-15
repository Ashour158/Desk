"""
Add table partitioning for improved performance with large datasets.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_add_fulltext_search_indexes'),
    ]

    operations = [
        # Create partitioned table for ticket history (by month)
        migrations.RunSQL(
            """
            -- Create partitioned table for ticket history
            CREATE TABLE IF NOT EXISTS tickets_tickethistory_partitioned (
                LIKE tickets_tickethistory INCLUDING ALL
            ) PARTITION BY RANGE (created_at);
            
            -- Create monthly partitions for the last 12 months
            DO $$
            DECLARE
                start_date date;
                end_date date;
                partition_name text;
            BEGIN
                -- Create partitions for the last 12 months
                FOR i IN 0..11 LOOP
                    start_date := date_trunc('month', CURRENT_DATE - INTERVAL '1 month' * i);
                    end_date := start_date + INTERVAL '1 month';
                    partition_name := 'tickets_tickethistory_' || to_char(start_date, 'YYYY_MM');
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF tickets_tickethistory_partitioned
                        FOR VALUES FROM (%L) TO (%L)
                    ', partition_name, start_date, end_date);
                END LOOP;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS tickets_tickethistory_partitioned CASCADE;
            """
        ),
        
        # Create partitioned table for ticket comments (by month)
        migrations.RunSQL(
            """
            -- Create partitioned table for ticket comments
            CREATE TABLE IF NOT EXISTS tickets_ticketcomment_partitioned (
                LIKE tickets_ticketcomment INCLUDING ALL
            ) PARTITION BY RANGE (created_at);
            
            -- Create monthly partitions for the last 12 months
            DO $$
            DECLARE
                start_date date;
                end_date date;
                partition_name text;
            BEGIN
                -- Create partitions for the last 12 months
                FOR i IN 0..11 LOOP
                    start_date := date_trunc('month', CURRENT_DATE - INTERVAL '1 month' * i);
                    end_date := start_date + INTERVAL '1 month';
                    partition_name := 'tickets_ticketcomment_' || to_char(start_date, 'YYYY_MM');
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF tickets_ticketcomment_partitioned
                        FOR VALUES FROM (%L) TO (%L)
                    ', partition_name, start_date, end_date);
                END LOOP;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS tickets_ticketcomment_partitioned CASCADE;
            """
        ),
        
        # Create partitioned table for user sessions (by month)
        migrations.RunSQL(
            """
            -- Create partitioned table for user sessions
            CREATE TABLE IF NOT EXISTS accounts_usersession_partitioned (
                LIKE accounts_usersession INCLUDING ALL
            ) PARTITION BY RANGE (created_at);
            
            -- Create monthly partitions for the last 12 months
            DO $$
            DECLARE
                start_date date;
                end_date date;
                partition_name text;
            BEGIN
                -- Create partitions for the last 12 months
                FOR i IN 0..11 LOOP
                    start_date := date_trunc('month', CURRENT_DATE - INTERVAL '1 month' * i);
                    end_date := start_date + INTERVAL '1 month';
                    partition_name := 'accounts_usersession_' || to_char(start_date, 'YYYY_MM');
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF accounts_usersession_partitioned
                        FOR VALUES FROM (%L) TO (%L)
                    ', partition_name, start_date, end_date);
                END LOOP;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS accounts_usersession_partitioned CASCADE;
            """
        ),
        
        # Create partitioned table for ticket attachments (by organization)
        migrations.RunSQL(
            """
            -- Create partitioned table for ticket attachments
            CREATE TABLE IF NOT EXISTS tickets_ticketattachment_partitioned (
                LIKE tickets_ticketattachment INCLUDING ALL
            ) PARTITION BY HASH (ticket_id);
            
            -- Create hash partitions (8 partitions for good distribution)
            DO $$
            DECLARE
                i int;
                partition_name text;
            BEGIN
                FOR i IN 0..7 LOOP
                    partition_name := 'tickets_ticketattachment_part_' || i;
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF tickets_ticketattachment_partitioned
                        FOR VALUES WITH (modulus 8, remainder %s)
                    ', partition_name, i);
                END LOOP;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS tickets_ticketattachment_partitioned CASCADE;
            """
        ),
        
        # Create partitioned table for user permissions (by user)
        migrations.RunSQL(
            """
            -- Create partitioned table for user permissions
            CREATE TABLE IF NOT EXISTS accounts_userpermission_partitioned (
                LIKE accounts_userpermission INCLUDING ALL
            ) PARTITION BY HASH (user_id);
            
            -- Create hash partitions (4 partitions for good distribution)
            DO $$
            DECLARE
                i int;
                partition_name text;
            BEGIN
                FOR i IN 0..3 LOOP
                    partition_name := 'accounts_userpermission_part_' || i;
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF accounts_userpermission_partitioned
                        FOR VALUES WITH (modulus 4, remainder %s)
                    ', partition_name, i);
                END LOOP;
            END $$;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS accounts_userpermission_partitioned CASCADE;
            """
        ),
        
        # Create function to automatically create new partitions
        migrations.RunSQL(
            """
            -- Function to create new monthly partitions
            CREATE OR REPLACE FUNCTION create_monthly_partition(
                table_name text,
                partition_date date
            ) RETURNS void AS $$
            DECLARE
                partition_name text;
                start_date date;
                end_date date;
            BEGIN
                start_date := date_trunc('month', partition_date);
                end_date := start_date + INTERVAL '1 month';
                partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
                
                EXECUTE format('
                    CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
                    FOR VALUES FROM (%L) TO (%L)
                ', partition_name, table_name, start_date, end_date);
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS create_monthly_partition(text, date);"
        ),
        
        # Create function to automatically create new hash partitions
        migrations.RunSQL(
            """
            -- Function to create new hash partitions
            CREATE OR REPLACE FUNCTION create_hash_partition(
                table_name text,
                partition_count int
            ) RETURNS void AS $$
            DECLARE
                i int;
                partition_name text;
            BEGIN
                FOR i IN 0..(partition_count - 1) LOOP
                    partition_name := table_name || '_part_' || i;
                    
                    EXECUTE format('
                        CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
                        FOR VALUES WITH (modulus %s, remainder %s)
                    ', partition_name, table_name, partition_count, i);
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS create_hash_partition(text, int);"
        ),
        
        # Create function to drop old partitions
        migrations.RunSQL(
            """
            -- Function to drop old partitions (older than retention period)
            CREATE OR REPLACE FUNCTION drop_old_partitions(
                table_name text,
                retention_months int DEFAULT 12
            ) RETURNS void AS $$
            DECLARE
                partition_name text;
                cutoff_date date;
            BEGIN
                cutoff_date := CURRENT_DATE - INTERVAL '1 month' * retention_months;
                
                -- Get list of partitions older than cutoff
                FOR partition_name IN
                    SELECT schemaname||'.'||tablename
                    FROM pg_tables
                    WHERE tablename LIKE table_name || '_%'
                    AND tablename ~ '^' || table_name || '_[0-9]{4}_[0-9]{2}$'
                    AND tablename < table_name || '_' || to_char(cutoff_date, 'YYYY_MM')
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || partition_name || ' CASCADE';
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS drop_old_partitions(text, int);"
        ),
    ]
