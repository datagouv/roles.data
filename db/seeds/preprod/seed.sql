\set schema_name :DB_SCHEMA

-- Seed data for development environment

-- Create an organization for the group
INSERT INTO :schema_name.organisations (id, name, siren)
VALUES (1, 'DINUM', '130020649') ON CONFLICT (id) DO NOTHING;

-- Create the "stack technique" group
INSERT INTO :schema_name.groups (id, name, orga_id)
VALUES (1, 'stack technique', 1) ON CONFLICT (id) DO NOTHING;

-- Create 5 users with different emails
INSERT INTO :schema_name.users (id, email, is_email_confirmed)
VALUES
  (1, 'user@yopmail.com', false),
  (2, 'xavier.jouppe@beta.gouv.fr', false),
  (3, 'robin.monnier@beta.gouv.fr', false),
  (4, 'hajar.ait-el-kadi@beta.gouv.fr', false),
  (5, 'amandine.audras@beta.gouv.fr', false) ON CONFLICT (id) DO NOTHING;

-- Create the service provider "test"
INSERT INTO :schema_name.service_providers (id, name)
VALUES (1, 'droles_test') ON CONFLICT (id) DO NOTHING;

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
INSERT INTO :schema_name.group_service_provider_relations (service_provider_id, group_id, scopes)
VALUES (1, 1, 'administrateur rne nonDiffusible conformite beneficiaires agent pseudo_opendata effectifs_annuels chiffre_affaires travaux_publics liens_capitalistiques liasses_fiscales bilans_bdf') ON CONFLICT (service_provider_id, group_id) DO NOTHING;

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
) ON CONFLICT DO NOTHING;
