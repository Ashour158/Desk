# Generated manually for adding SLA performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_add_materialized_views'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['assigned_agent', 'status'], name='tickets_ticket_assigned_agent_status_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['sla_policy'], name='tickets_ticket_sla_policy_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['first_response_due'], name='tickets_ticket_first_response_due_idx'),
        ),
        migrations.AddIndex(
            model_name='ticket',
            index=models.Index(fields=['resolution_due'], name='tickets_ticket_resolution_due_idx'),
        ),
    ]
