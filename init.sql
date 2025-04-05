-- Initialize extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS app;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create roles
CREATE ROLE app_admin WITH LOGIN PASSWORD 'change_me_in_production';
CREATE ROLE app_user WITH LOGIN PASSWORD 'change_me_in_production';
CREATE ROLE auditor WITH LOGIN PASSWORD 'change_me_in_production';

-- Create audit tables
CREATE TABLE audit.activity_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT,
    action TEXT,
    table_name TEXT,
    record_id TEXT,
    old_data JSONB,
    new_data JSONB
);

-- Create application tables with encryption
CREATE TABLE app.users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    encrypted_ssn BYTEA,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security
ALTER TABLE app.users ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies
CREATE POLICY users_self_access ON app.users
    USING (username = current_user);