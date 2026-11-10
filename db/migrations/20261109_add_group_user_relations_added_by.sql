\set schema_name :DB_SCHEMA

-- Track which user added a user to a group. NULL when unknown: rows created
-- before this column, or users added by a service provider or the admin interface.
ALTER TABLE :schema_name.group_user_relations
ADD COLUMN added_by INTEGER NULL,
ADD CONSTRAINT group_user_fk_relation_added_by FOREIGN KEY (added_by) REFERENCES :schema_name.users (id) ON DELETE SET NULL;

-- Backfill added_by from the audit logs of users added by a group admin through
-- the resource server.
-- * A relation and its log are written in the same transaction, so they share
--   the same created_at: this matches the log of the current relation, even for
--   a user removed then added again.
-- * service_provider_id = 0 is the admin interface, left out as the application
--   does not record it either. The service provider API and the DataPass webhook
--   log no acting user, and so are left out by the join on users.
-- * Logs before 2025-07-09 carry no acting user, those relations stay NULL.
UPDATE :schema_name.group_user_relations AS GUR
SET added_by = U.id
FROM :schema_name.audit_logs AS A
INNER JOIN :schema_name.users AS U ON U.sub_pro_connect = A.acting_user_sub
WHERE A.action_type = 'ADD_USER_TO_GROUP'
  AND A.resource_type = 'GROUP'
  AND A.service_provider_id <> 0
  AND A.resource_id = GUR.group_id
  AND (A.new_values->>'user_id')::int = GUR.user_id
  AND A.created_at = GUR.created_at
  AND GUR.added_by IS NULL
  AND U.id <> GUR.user_id;
