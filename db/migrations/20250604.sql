\set schema_name :DB_SCHEMA

BEGIN;

ALTER TABLE :schema_name.users
RENAME COLUMN is_email_confirmed TO is_verified;

COMMIT;
