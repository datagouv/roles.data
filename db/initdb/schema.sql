\set ON_ERROR_STOP on
SET temp.schema_name = :DB_SCHEMA;


DO $$
DECLARE
   schema_name text := current_setting('temp.schema_name');
   table_count integer;
BEGIN
   -- Check if schema exists and count tables in it
   SELECT COUNT(*)
   INTO table_count
   FROM information_schema.tables
   WHERE table_schema = schema_name
   AND table_type = 'BASE TABLE';

   RAISE NOTICE 'Found % tables in schema "%"', table_count, schema_name;

   -- If schema has tables, skip creation
   IF table_count > 0 THEN
      RAISE NOTICE 'Schema "%" already contains % table(s)', schema_name, table_count;
      RAISE NOTICE 'Skipping schema creation';
      RETURN; -- Exit the DO block
   END IF;

   RAISE NOTICE 'Schema "%" is empty or doesn''t exist', schema_name;
   RAISE NOTICE 'Proceeding with schema creation...';

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
