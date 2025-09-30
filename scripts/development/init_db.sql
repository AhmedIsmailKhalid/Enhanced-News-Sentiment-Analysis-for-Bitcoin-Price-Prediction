-- Bitcoin Sentiment MLOps Database Initialization
-- Creates extensions and basic setup

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas for data organization
CREATE SCHEMA IF NOT EXISTS production;
CREATE SCHEMA IF NOT EXISTS testing;

-- Set default schema
SET search_path TO public;

-- Create function for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully';
END $$;