\set schema_name :DB_SCHEMA

BEGIN;

-- Remove NOT NULL constraint from name column in organisations table
ALTER TABLE :schema_name.organisations
ALTER COLUMN name DROP NOT NULL;

-- Optional: Add a comment to document the change
COMMENT ON COLUMN :schema_name.organisations.name IS 'Organisation name - can be NULL if not yet fetched from API';

COMMIT;
