\set schema_name :DB_SCHEMA

--  see migration 20250815
INSERT INTO :schema_name.roles (id, role_name, is_admin) VALUES
(1, 'administrateur', true),
(2, 'agent', false),
(3, 'prestataire', false) ON CONFLICT (id) DO NOTHING;
