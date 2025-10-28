\set schema_name :DB_SCHEMA

ALTER TABLE :schema_name.users
DROP COLUMN is_verified;
