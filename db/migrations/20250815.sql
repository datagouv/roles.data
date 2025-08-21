\set schema_name :DB_SCHEMA

-- Fourth prestataire remove

-- Issue was, roles were seeded in the create.sql as it is a metadata used in every environnement.

-- As the create.sql is always ran but the migration is only ran once, it would get re-added on each following deployment.
-- With migration 20250501.sql we ensure it gets provisionned right after the create. But it only get run once.

UPDATE :schema_name.group_user_relations
SET role_id = 2
WHERE role_id = 3;

-- Remove the "prestataire" role from the roles table
DELETE FROM :schema_name.roles
WHERE id = 3;
