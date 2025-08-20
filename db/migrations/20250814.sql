\set schema_name :DB_SCHEMA

-- Third prestataire remove as it does NOT work

-- First, update all users who have the "prestataire" role (id=3) to use "utilisateur" role (id=2)
UPDATE :schema_name.group_user_relations
SET role_id = 2
WHERE role_id = 3;

-- Remove the "prestataire" role from the roles table
DELETE FROM :schema_name.roles
WHERE id = 3;
