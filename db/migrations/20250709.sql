\set schema_name :DB_SCHEMA

ALTER TABLE :schema_name.audit_logs
ADD COLUMN acting_user_sub VARCHAR(255);
