\set schema_name :DB_SCHEMA

-- First, rename the column
ALTER TABLE :schema_name.service_accounts
RENAME COLUMN deactivated TO is_active;

-- Then, invert the boolean values (since deactivated=false means is_active=true)
UPDATE :schema_name.service_accounts
SET is_active = NOT is_active;

-- Update the roles
DELETE FROM :schema_name.roles WHERE id = 3;

UPDATE :schema_name.roles SET role_name = 'utilisateur' WHERE id = 2;
