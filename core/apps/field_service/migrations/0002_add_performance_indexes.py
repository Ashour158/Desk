"""
Add performance indexes for field service models.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field_service', '0001_initial'),
    ]

    operations = [
        # Add composite indexes for work orders
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_org_status_priority ON work_orders (organization_id, status, priority);",
            reverse_sql="DROP INDEX IF EXISTS idx_work_orders_org_status_priority;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_org_created_status ON work_orders (organization_id, created_at, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_work_orders_org_created_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_work_orders_customer_created ON work_orders (customer_id, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_work_orders_customer_created;"
        ),
        
        # Add indexes for job assignments
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_assignments_work_order ON field_service_jobassignment (work_order_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_job_assignments_work_order;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_assignments_technician ON field_service_jobassignment (technician_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_job_assignments_technician;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_assignments_status_created ON field_service_jobassignment (status, created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_job_assignments_status_created;"
        ),
        
        # Add indexes for technicians
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technicians_org_status ON field_service_technician (organization_id, availability_status);",
            reverse_sql="DROP INDEX IF EXISTS idx_technicians_org_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technicians_skills ON field_service_technician USING GIN (skills);",
            reverse_sql="DROP INDEX IF EXISTS idx_technicians_skills;"
        ),
        
        # Add indexes for assets
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assets_org_status ON field_service_asset (organization_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_assets_org_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_assets_next_service ON field_service_asset (next_service_date) WHERE next_service_date IS NOT NULL;",
            reverse_sql="DROP INDEX IF EXISTS idx_assets_next_service;"
        ),
        
        # Add indexes for inventory
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_org_status ON field_service_inventoryitem (organization_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_inventory_org_status;"
        ),
        
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventory_low_stock ON field_service_inventoryitem (organization_id, is_low_stock) WHERE is_low_stock = true;",
            reverse_sql="DROP INDEX IF EXISTS idx_inventory_low_stock;"
        ),
        
        # Add indexes for routes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_routes_technician_date ON field_service_route (technician_id, route_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_routes_technician_date;"
        ),
    ]
