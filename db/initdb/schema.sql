\set ON_ERROR_STOP on
SET temp.schema_name = :DB_SCHEMA;


DO $$
DECLARE
   schema_name text := current_setting('temp.schema_name');
BEGIN
   EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_name);
EXCEPTION
   WHEN insufficient_privilege THEN
      IF NOT EXISTS (
         SELECT 1 FROM pg_namespace WHERE nspname = schema_name
      ) THEN
         RAISE EXCEPTION 'Insufficient privilege to create schema "%", and it does not exist.',schema_name;
      ELSE
         RAISE NOTICE 'Schema "%" already exists but cannot be created due to insufficient privileges. Continuing.',schema_name;
      END IF;
   WHEN OTHERS THEN
      -- Re-raise any other exception (this will cause the script to fail)
      RAISE;
END;
$$;
