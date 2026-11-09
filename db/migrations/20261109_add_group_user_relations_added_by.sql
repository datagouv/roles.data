\set schema_name :DB_SCHEMA

-- Track which user added a user to a group. NULL when unknown: rows created
-- before this column, or users added by a service provider or the admin interface.
ALTER TABLE :schema_name.group_user_relations
ADD COLUMN added_by INTEGER NULL,
ADD CONSTRAINT group_user_fk_relation_added_by FOREIGN KEY (added_by) REFERENCES :schema_name.users (id) ON DELETE SET NULL;
