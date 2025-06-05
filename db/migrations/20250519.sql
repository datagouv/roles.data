\set schema_name :DB_SCHEMA

BEGIN;

ALTER TABLE :schema_name.group_service_provider_relations
ADD COLUMN contract TEXT NOT NULL DEFAULT '';

-- Add this after your table creation
ALTER TABLE :schema_name.service_accounts
ADD CONSTRAINT service_accounts_provider_name_unique UNIQUE (service_provider_id, name);

COMMIT;
