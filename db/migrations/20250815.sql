\set schema_name :DB_SCHEMA

-- Fourth prestataire remove

-- Issue was, prestataire were seeds in the create.sql as it is metadata,
-- not an actual seed and therefore used in every environnement.

-- As the create is always run but the migration was only ran once. It would get readded on each following deployment.
-- With migration 20250501.sql we ensure it gets provisionned right after the create. But it only get run once.

UPDATE :schema_name.group_user_relations
SET role_id = 2
WHERE role_id = 3;

-- Remove the "prestataire" role from the roles table
DELETE FROM :schema_name.roles
WHERE id = 3;
