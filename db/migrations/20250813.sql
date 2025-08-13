\set schema_name :DB_SCHEMA

-- Migration: Convert all emails to lowercase
-- Date: 2025-08-13

-- Update all emails in users table to lowercase
UPDATE :schema_name.users
SET email = LOWER(email)
WHERE email != LOWER(email);
