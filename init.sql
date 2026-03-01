-- Database initialization script for Attendance Dashboard
-- This script runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set default timezone
SET timezone = 'UTC';

-- Create indexes for performance (in addition to model-defined ones)
-- These are created after tables by SQLAlchemy, but we can add additional ones here

-- Composite index for common dashboard queries
-- CREATE INDEX IF NOT EXISTS idx_dashboard_summary 
-- ON attendance_records(student_id, is_present, date);

-- Index for monthly trend calculations
-- CREATE INDEX IF NOT EXISTS idx_monthly_trend 
-- ON attendance_records(date, student_id, is_present);

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
END $$;
