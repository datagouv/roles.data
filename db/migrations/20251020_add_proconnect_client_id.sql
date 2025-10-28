\set schema_name :DB_SCHEMA

-- Add proconnect_client_id column to service_providers table
ALTER TABLE :schema_name.service_providers
ADD COLUMN proconnect_client_id VARCHAR(255) UNIQUE;

-- Add index for faster lookups by proconnect_client_id
CREATE INDEX idx_service_providers_proconnect_client_id
ON :schema_name.service_providers(proconnect_client_id);
