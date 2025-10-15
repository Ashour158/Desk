-- Initialize database with sequences and extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Create sequences for ticket and work order numbers
CREATE SEQUENCE IF NOT EXISTS ticket_number_seq START 1;
CREATE SEQUENCE IF NOT EXISTS work_order_number_seq START 1;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_users_email_org ON users(email, organization_id);
CREATE INDEX IF NOT EXISTS idx_tickets_org_status ON tickets(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_tickets_org_priority ON tickets(organization_id, priority);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_agent ON tickets(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_work_orders_org_status ON work_orders(organization_id, status);
CREATE INDEX IF NOT EXISTS idx_work_orders_customer ON work_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_technicians_org ON technicians(organization_id);
CREATE INDEX IF NOT EXISTS idx_technicians_user ON technicians(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_org_time ON activity_logs(organization_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_activity_logs_entity ON activity_logs(entity_type, entity_id);

-- Create GIN indexes for JSONB fields
CREATE INDEX IF NOT EXISTS idx_organizations_settings ON organizations USING GIN(settings);
CREATE INDEX IF NOT EXISTS idx_tickets_custom_fields ON tickets USING GIN(custom_fields);
CREATE INDEX IF NOT EXISTS idx_tickets_tags ON tickets USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_work_orders_custom_fields ON work_orders USING GIN(custom_fields);
CREATE INDEX IF NOT EXISTS idx_technicians_skills ON technicians USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_technicians_certifications ON technicians USING GIN(certifications);

-- Create spatial indexes for PostGIS
CREATE INDEX IF NOT EXISTS idx_technicians_location ON technicians USING GIST(current_location);
CREATE INDEX IF NOT EXISTS idx_work_orders_location ON work_orders USING GIST(location_coordinates);

-- Set up Row Level Security (RLS) for multi-tenancy
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE work_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE technicians ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE automation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (these will be managed by Django)
-- Note: Django will handle the actual RLS policy creation through migrations
