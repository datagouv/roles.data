\set schema_name :DB_SCHEMA

CREATE INDEX IF NOT EXISTS idx_service_accounts_name ON :schema_name.service_accounts(name);
CREATE INDEX IF NOT EXISTS idx_service_accounts_is_active ON :schema_name.service_accounts(is_active);

-- Groups references organisations
CREATE INDEX IF NOT EXISTS idx_groups_orga_id ON :schema_name.groups(orga_id);

-- Group user relations
CREATE INDEX IF NOT EXISTS idx_group_user_relations_group_id ON :schema_name.group_user_relations(group_id);
CREATE INDEX IF NOT EXISTS idx_group_user_relations_user_id ON :schema_name.group_user_relations(user_id);
CREATE INDEX IF NOT EXISTS idx_group_user_relations_role_id ON :schema_name.group_user_relations(role_id);

-- Group service provider relations
CREATE INDEX IF NOT EXISTS idx_group_service_provider_relations_group_id ON :schema_name.group_service_provider_relations(group_id);
CREATE INDEX IF NOT EXISTS idx_group_service_provider_relations_service_provider_id ON :schema_name.group_service_provider_relations(service_provider_id);

-- Service accounts
CREATE INDEX IF NOT EXISTS idx_service_accounts_service_provider_id ON :schema_name.service_accounts(service_provider_id);

-- Parent child relations
CREATE INDEX IF NOT EXISTS idx_parent_child_relations_parent_group_id ON :schema_name.parent_child_relations(parent_group_id);
CREATE INDEX IF NOT EXISTS idx_parent_child_relations_child_group_id ON :schema_name.parent_child_relations(child_group_id);
