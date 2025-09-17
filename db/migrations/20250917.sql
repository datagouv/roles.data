\set schema_name :DB_SCHEMA

-- Add Datapass service provider
-- Datapass is a hardcoded provider that can create groups for other service providers

BEGIN;

-- Insert Datapass service provider
INSERT INTO :schema_name.service_providers (id, name, url)
VALUES (999, 'Datapass', 'https://datapass.api.gouv.fr');

COMMIT;
