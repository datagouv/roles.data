\set schema_name :DB_SCHEMA

BEGIN;

ALTER TABLE :schema_name.users
RENAME COLUMN is_email_confirmed TO is_verified;

ALTER TABLE :schema_name.users
ADD CONSTRAINT users_sub_pro_connect_unique UNIQUE (sub_pro_connect)
WHERE sub_pro_connect IS NOT NULL;

COMMIT;
