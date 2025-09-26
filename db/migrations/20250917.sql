\set schema_name :DB_SCHEMA

-- Add Datapass service provider
-- Datapass is a hardcoded provider that can create groups for other service providers
-- This constant should match DATAPASS_SERVICE_PROVIDER_ID in src/constants.py

\set datapass_id 999

BEGIN;

-- Insert Datapass service provider
INSERT INTO :schema_name.service_providers (id, name, url)
VALUES (:datapass_id, 'Datapass', 'https://datapass.api.gouv.fr');

COMMIT;
