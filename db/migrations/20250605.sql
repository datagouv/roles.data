\set schema_name :DB_SCHEMA

CREATE UNIQUE INDEX users_sub_pro_connect_unique_idx
ON :schema_name.users (sub_pro_connect)
WHERE sub_pro_connect IS NOT NULL;
