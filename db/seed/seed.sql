\set schema_name :DB_SCHEMA

-- Seed data for development & test environment

-- Begin transaction
BEGIN;

-- Create an organization for the group
INSERT INTO :schema_name.organisations (id, name, siret)
VALUES (1, 'DINUM', '13002526500013') ON CONFLICT (id) DO NOTHING;

-- Create the "stack technique" group
INSERT INTO :schema_name.groups (id, name, orga_id)
VALUES (1, 'stack technique', 1) ON CONFLICT (id) DO NOTHING;

-- Create users with different emails
INSERT INTO :schema_name.users (id, email, is_verified)
VALUES
  (1, 'user@yopmail.com', false),
  (2, 'xavier.jouppe@beta.gouv.fr', false),
  (3, 'robin.monnier@beta.gouv.fr', false),
  (4, 'hajar.ait-el-kadi@beta.gouv.fr', false),
  (6, 'user-not-in-group@beta.gouv.fr', false),
  (5, 'amandine.audras@beta.gouv.fr', false) ON CONFLICT (id) DO NOTHING;

-- Create the service provider "test"
INSERT INTO :schema_name.service_providers (id, name, url)
VALUES (1, 'droles-test', 'https://data.gouv.fr') ON CONFLICT (id) DO NOTHING;

-- Add the users to the group with their respective roles
-- User 1 is an admin (role_id = 1)
-- Others are agents (role_id = 2)
INSERT INTO :schema_name.group_user_relations (group_id, user_id, role_id)
VALUES
  (1, 1, 1),
  (1, 2, 2),
  (1, 3, 2),
  (1, 4, 2),
  (1, 5, 2) ON CONFLICT (group_id, user_id) DO NOTHING;

-- Add the "read" scope for the group on the service provider "test"
INSERT INTO :schema_name.group_service_provider_relations (service_provider_id, group_id, scopes, contract_description, contract_url)
VALUES (1, 1, 'administrateur rne nonDiffusible conformite beneficiaires agent pseudo_opendata effectifs_annuels chiffre_affaires travaux_publics liens_capitalistiques liasses_fiscales bilans_bdf', 'Habilitation de test', 'https://datapass_48') ON CONFLICT (service_provider_id, group_id) DO NOTHING;

-- Insert a service account for a service provider
INSERT INTO :schema_name.service_accounts (
    service_provider_id,
    name,
    hashed_password,
    is_active
)
VALUES (
    1,
    'client_id',
    '$2b$12$3NJuxRM4j5rnuXtKysMRiujPCd13Z5T5k4Bs7TSPWszFfpPgkyWRa',
    true
) ON CONFLICT (service_provider_id, name) DO NOTHING;

-- Update sequences to continue after our manually inserted IDs

-- First set a PostgreSQL session parameter with the schema name
SET temp.schema_name = :'schema_name';

DO $$
DECLARE
  schema_var text := current_setting('temp.schema_name');
BEGIN
  EXECUTE format('SELECT setval(%L, (SELECT COALESCE(MAX(id), 0) FROM %I.users), true)',
                 schema_var || '.users_id_seq', schema_var);
  EXECUTE format('SELECT setval(%L, (SELECT COALESCE(MAX(id), 0) FROM %I.groups), true)',
                 schema_var || '.groups_id_seq', schema_var);
  EXECUTE format('SELECT setval(%L, (SELECT COALESCE(MAX(id), 0) FROM %I.organisations), true)',
                 schema_var || '.organisations_id_seq', schema_var);
  EXECUTE format('SELECT setval(%L, (SELECT COALESCE(MAX(id), 0) FROM %I.service_providers), true)',
                 schema_var || '.service_providers_id_seq', schema_var);
  EXECUTE format('SELECT setval(%L, (SELECT COALESCE(MAX(id), 0) FROM %I.service_accounts), true)',
                 schema_var || '.service_accounts_id_seq', schema_var);
END;
$$;

COMMIT;
