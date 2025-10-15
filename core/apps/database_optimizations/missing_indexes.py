"""
Database migration to add missing critical indexes for query optimization.
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Add missing critical indexes for query optimization.
    """

    dependencies = [
        ('knowledge_base', '0001_initial'),
        ('field_service', '0001_initial'),
        ('communication_platform', '0001_initial'),
        ('advanced_analytics', '0001_initial'),
        ('ai_ml', '0001_initial'),
    ]

    operations = [
        # Knowledge Base indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_kb_articles_org_status_published ON knowledge_base_kbarticle (organization_id, status, published_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_kb_articles_org_status_published;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_kb_articles_category_views ON knowledge_base_kbarticle (category_id, view_count);",
            reverse_sql="DROP INDEX IF EXISTS idx_kb_articles_category_views;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_kb_articles_search ON knowledge_base_kbarticle USING gin(to_tsvector('english', title || ' ' || content));",
            reverse_sql="DROP INDEX IF EXISTS idx_kb_articles_search;"
        ),
        
        # Field Service indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_technician_status ON work_orders (technician_id, status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_work_orders_technician_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technicians_org_skills ON field_service_technician USING gin(skills);",
            reverse_sql="DROP INDEX IF EXISTS idx_technicians_skills;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technicians_org_availability ON field_service_technician (organization_id, availability_status, last_seen);",
            reverse_sql="DROP INDEX IF EXISTS idx_technicians_org_availability;"
        ),
        
        # Communication Platform indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communication_logs_org_type ON communication_platform_communicationlog (organization_id, log_type, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_communication_logs_org_type;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_communication_messages_session ON communication_platform_communicationmessage (session_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_communication_messages_session;"
        ),
        
        # Advanced Analytics indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_metrics_org_date ON advanced_analytics_analyticsmetric (organization_id, metric_date, metric_name);",
            reverse_sql="DROP INDEX IF EXISTS idx_analytics_metrics_org_date;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analytics_reports_org_type ON advanced_analytics_analyticsreport (organization_id, report_type, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_analytics_reports_org_type;"
        ),
        
        # AI/ML indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_models_org_status ON ai_ml_aimodel (organization_id, status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_ai_models_org_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_predictions_model_date ON ai_ml_aiprediction (model_id, prediction_date, confidence_score);",
            reverse_sql="DROP INDEX IF EXISTS idx_ai_predictions_model_date;"
        ),
        
        # User and Organization indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_org_role ON accounts_user (organization_id, role, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_users_org_role;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_organizations_domain ON organizations_organization (domain, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_organizations_domain;"
        ),
        
        # Automation indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_automation_rules_org_active ON automation_automationrule (organization_id, is_active, priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_automation_rules_org_active;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_automation_executions_rule_date ON automation_automationexecution (rule_id, executed_at, success);",
            reverse_sql="DROP INDEX IF EXISTS idx_automation_executions_rule_date;"
        ),
        
        # Workflow indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workflow_executions_org_status ON workflow_automation_workflowexecution (organization_id, status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_workflow_executions_org_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workflow_steps_execution ON workflow_automation_workflowstep (execution_id, step_order, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_workflow_steps_execution;"
        ),
        
        # Integration indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_integrations_org_type ON integration_platform_integration (organization_id, integration_type, is_active);",
            reverse_sql="DROP INDEX IF EXISTS idx_integrations_org_type;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_integration_logs_org_severity ON integration_platform_integrationlog (organization_id, severity, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_integration_logs_org_severity;"
        ),
        
        # Mobile/IoT indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_mobile_sessions_org_user ON mobile_iot_mobilesession (organization_id, user_id, session_status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_mobile_sessions_org_user;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_datapoints_device_date ON mobile_iot_iotdatapoint (device_id, timestamp, data_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_iot_datapoints_device_date;"
        ),
        
        # Security indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_events_org_type ON security_securityevent (organization_id, event_type, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_security_events_org_type;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_org_user ON security_auditlog (organization_id, user_id, action, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_audit_logs_org_user;"
        ),
        
        # Customer Experience indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feedback_org_rating ON customer_experience_feedback (organization_id, rating, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_feedback_org_rating;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_surveys_org_status ON customer_experience_survey (organization_id, status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_surveys_org_status;"
        ),
        
        # Partial indexes for performance
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tickets_high_priority ON tickets_ticket (organization_id, created_at) WHERE priority IN ('high', 'urgent');",
            reverse_sql="DROP INDEX IF EXISTS idx_tickets_high_priority;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_overdue ON work_orders (organization_id, due_date) WHERE status NOT IN ('completed', 'cancelled') AND due_date < NOW();",
            reverse_sql="DROP INDEX IF EXISTS idx_work_orders_overdue;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_kb_articles_popular ON knowledge_base_kbarticle (view_count, helpful_count) WHERE status = 'published' AND view_count > 0;",
            reverse_sql="DROP INDEX IF EXISTS idx_kb_articles_popular;"
        ),
    ]

