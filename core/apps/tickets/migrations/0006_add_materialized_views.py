"""
Add materialized views for dashboard statistics and reporting.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_add_table_partitioning'),
    ]

    operations = [
        # Create materialized view for organization dashboard statistics
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW dashboard_stats AS
            SELECT 
                t.organization_id,
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE t.status = 'new') as new_tickets,
                COUNT(*) FILTER (WHERE t.status = 'open') as open_tickets,
                COUNT(*) FILTER (WHERE t.status = 'pending') as pending_tickets,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved_tickets,
                COUNT(*) FILTER (WHERE t.status = 'closed') as closed_tickets,
                COUNT(*) FILTER (WHERE t.status = 'cancelled') as cancelled_tickets,
                COUNT(*) FILTER (WHERE t.priority = 'low') as low_priority_tickets,
                COUNT(*) FILTER (WHERE t.priority = 'medium') as medium_priority_tickets,
                COUNT(*) FILTER (WHERE t.priority = 'high') as high_priority_tickets,
                COUNT(*) FILTER (WHERE t.priority = 'urgent') as urgent_tickets,
                COUNT(*) FILTER (WHERE t.sla_breach = true) as sla_breach_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                AVG(EXTRACT(EPOCH FROM (t.first_response_at - t.created_at))/3600) FILTER (WHERE t.first_response_at IS NOT NULL) as avg_first_response_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as tickets_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as tickets_last_30_days,
                COUNT(*) FILTER (WHERE t.resolved_at >= CURRENT_DATE - INTERVAL '7 days') as resolved_last_7_days,
                COUNT(*) FILTER (WHERE t.resolved_at >= CURRENT_DATE - INTERVAL '30 days') as resolved_last_30_days,
                MAX(t.created_at) as last_ticket_created,
                MAX(t.resolved_at) as last_ticket_resolved,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            GROUP BY t.organization_id;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS dashboard_stats;"
        ),
        
        # Create materialized view for agent performance statistics
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW agent_performance_stats AS
            SELECT 
                t.assigned_agent_id,
                t.organization_id,
                COUNT(*) as total_assigned_tickets,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved_tickets,
                COUNT(*) FILTER (WHERE t.status = 'closed') as closed_tickets,
                COUNT(*) FILTER (WHERE t.sla_breach = true) as sla_breach_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                AVG(EXTRACT(EPOCH FROM (t.first_response_at - t.created_at))/3600) FILTER (WHERE t.first_response_at IS NOT NULL) as avg_first_response_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as assigned_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as assigned_last_30_days,
                COUNT(*) FILTER (WHERE t.resolved_at >= CURRENT_DATE - INTERVAL '7 days') as resolved_last_7_days,
                COUNT(*) FILTER (WHERE t.resolved_at >= CURRENT_DATE - INTERVAL '30 days') as resolved_last_30_days,
                MAX(t.created_at) as last_ticket_assigned,
                MAX(t.resolved_at) as last_ticket_resolved,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            WHERE t.assigned_agent_id IS NOT NULL
            GROUP BY t.assigned_agent_id, t.organization_id;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS agent_performance_stats;"
        ),
        
        # Create materialized view for customer statistics
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW customer_stats AS
            SELECT 
                t.customer_id,
                t.organization_id,
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE t.status = 'open') as open_tickets,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved_tickets,
                COUNT(*) FILTER (WHERE t.status = 'closed') as closed_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as tickets_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as tickets_last_30_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '90 days') as tickets_last_90_days,
                MAX(t.created_at) as last_ticket_created,
                MAX(t.resolved_at) as last_ticket_resolved,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            GROUP BY t.customer_id, t.organization_id;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS customer_stats;"
        ),
        
        # Create materialized view for SLA performance
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW sla_performance_stats AS
            SELECT 
                t.organization_id,
                COUNT(*) as total_tickets_with_sla,
                COUNT(*) FILTER (WHERE t.first_response_due IS NOT NULL) as tickets_with_first_response_sla,
                COUNT(*) FILTER (WHERE t.resolution_due IS NOT NULL) as tickets_with_resolution_sla,
                COUNT(*) FILTER (WHERE t.sla_breach = true) as sla_breach_tickets,
                COUNT(*) FILTER (WHERE t.first_response_due IS NOT NULL AND t.first_response_at IS NOT NULL AND t.first_response_at <= t.first_response_due) as first_response_sla_met,
                COUNT(*) FILTER (WHERE t.resolution_due IS NOT NULL AND t.resolved_at IS NOT NULL AND t.resolved_at <= t.resolution_due) as resolution_sla_met,
                AVG(EXTRACT(EPOCH FROM (t.first_response_at - t.created_at))/3600) FILTER (WHERE t.first_response_at IS NOT NULL) as avg_first_response_hours,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as sla_tickets_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as sla_tickets_last_30_days,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            WHERE t.first_response_due IS NOT NULL OR t.resolution_due IS NOT NULL
            GROUP BY t.organization_id;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS sla_performance_stats;"
        ),
        
        # Create materialized view for ticket trends
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW ticket_trends AS
            SELECT 
                t.organization_id,
                DATE_TRUNC('day', t.created_at) as date,
                COUNT(*) as tickets_created,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as tickets_resolved,
                COUNT(*) FILTER (WHERE t.priority = 'urgent') as urgent_tickets,
                COUNT(*) FILTER (WHERE t.priority = 'high') as high_priority_tickets,
                COUNT(*) FILTER (WHERE t.sla_breach = true) as sla_breach_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            WHERE t.created_at >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY t.organization_id, DATE_TRUNC('day', t.created_at)
            ORDER BY t.organization_id, date;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS ticket_trends;"
        ),
        
        # Create materialized view for channel performance
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW channel_performance_stats AS
            SELECT 
                t.organization_id,
                t.channel,
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved_tickets,
                COUNT(*) FILTER (WHERE t.status = 'closed') as closed_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as tickets_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as tickets_last_30_days,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            GROUP BY t.organization_id, t.channel;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS channel_performance_stats;"
        ),
        
        # Create materialized view for category performance
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW category_performance_stats AS
            SELECT 
                t.organization_id,
                t.category,
                COUNT(*) as total_tickets,
                COUNT(*) FILTER (WHERE t.status = 'resolved') as resolved_tickets,
                COUNT(*) FILTER (WHERE t.status = 'closed') as closed_tickets,
                AVG(t.customer_satisfaction_score) FILTER (WHERE t.customer_satisfaction_score IS NOT NULL) as avg_satisfaction_score,
                AVG(EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600) FILTER (WHERE t.resolved_at IS NOT NULL) as avg_resolution_hours,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '7 days') as tickets_last_7_days,
                COUNT(*) FILTER (WHERE t.created_at >= CURRENT_DATE - INTERVAL '30 days') as tickets_last_30_days,
                CURRENT_TIMESTAMP as last_updated
            FROM tickets_ticket t
            WHERE t.category IS NOT NULL AND t.category != ''
            GROUP BY t.organization_id, t.category;
            """,
            reverse_sql="DROP MATERIALIZED VIEW IF EXISTS category_performance_stats;"
        ),
        
        # Create indexes on materialized views for better performance
        migrations.RunSQL(
            """
            CREATE INDEX IF NOT EXISTS idx_dashboard_stats_organization 
            ON dashboard_stats (organization_id);
            
            CREATE INDEX IF NOT EXISTS idx_agent_performance_stats_agent_org 
            ON agent_performance_stats (assigned_agent_id, organization_id);
            
            CREATE INDEX IF NOT EXISTS idx_customer_stats_customer_org 
            ON customer_stats (customer_id, organization_id);
            
            CREATE INDEX IF NOT EXISTS idx_sla_performance_stats_organization 
            ON sla_performance_stats (organization_id);
            
            CREATE INDEX IF NOT EXISTS idx_ticket_trends_org_date 
            ON ticket_trends (organization_id, date);
            
            CREATE INDEX IF NOT EXISTS idx_channel_performance_stats_org_channel 
            ON channel_performance_stats (organization_id, channel);
            
            CREATE INDEX IF NOT EXISTS idx_category_performance_stats_org_category 
            ON category_performance_stats (organization_id, category);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS idx_dashboard_stats_organization;
            DROP INDEX IF EXISTS idx_agent_performance_stats_agent_org;
            DROP INDEX IF EXISTS idx_customer_stats_customer_org;
            DROP INDEX IF EXISTS idx_sla_performance_stats_organization;
            DROP INDEX IF EXISTS idx_ticket_trends_org_date;
            DROP INDEX IF EXISTS idx_channel_performance_stats_org_channel;
            DROP INDEX IF EXISTS idx_category_performance_stats_org_category;
            """
        ),
        
        # Create function to refresh materialized views
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION refresh_dashboard_views() RETURNS void AS $$
            BEGIN
                REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY agent_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY customer_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY sla_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY ticket_trends;
                REFRESH MATERIALIZED VIEW CONCURRENTLY channel_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY category_performance_stats;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS refresh_dashboard_views();"
        ),
        
        # Create function to refresh specific organization views
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION refresh_organization_views(org_id int) RETURNS void AS $$
            BEGIN
                -- Refresh views for specific organization
                REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY agent_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY customer_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY sla_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY ticket_trends;
                REFRESH MATERIALIZED VIEW CONCURRENTLY channel_performance_stats;
                REFRESH MATERIALIZED VIEW CONCURRENTLY category_performance_stats;
            END;
            $$ LANGUAGE plpgsql;
            """,
            reverse_sql="DROP FUNCTION IF EXISTS refresh_organization_views(int);"
        ),
    ]
