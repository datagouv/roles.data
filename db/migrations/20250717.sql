\set schema_name :DB_SCHEMA

BEGIN;

-- Add URL column to service_providers table
ALTER TABLE :schema_name.service_providers
ADD COLUMN url VARCHAR(500) CHECK (url IS NULL OR url ~ '^https?://');

-- Add description column to group_service_provider_relations table
ALTER TABLE :schema_name.group_service_provider_relations
ADD COLUMN contract_url VARCHAR(500) CHECK (contract_url IS NULL OR contract_url ~ '^https?://');

-- Rename contract column to contract_description in group_service_provider_relations
ALTER TABLE :schema_name.group_service_provider_relations
RENAME COLUMN contract TO contract_description;


COMMIT;
