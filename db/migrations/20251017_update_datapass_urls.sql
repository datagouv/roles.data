\set schema_name :DB_SCHEMA

-- Update contract_url to remove 'production.' subdomain from datapass URLs
UPDATE :schema_name.group_service_provider_relations
SET contract_url = REPLACE(contract_url, 'https://production.datapass.api.gouv.fr/', 'https://datapass.api.gouv.fr/')
WHERE contract_url LIKE 'https://production.datapass.api.gouv.fr/%';
