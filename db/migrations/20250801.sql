\set schema_name :DB_SCHEMA

BEGIN;

CREATE INDEX idx_service_accounts_name ON service_accounts(name);
CREATE INDEX idx_service_accounts_deactivated ON service_accounts(deactivated) WHERE

-- Groups references organisations
CREATE INDEX idx_groups_orga_id ON groups(orga_id);

-- Group user relations
CREATE INDEX idx_group_user_relations_group_id ON group_user_relations(group_id);
CREATE INDEX idx_group_user_relations_user_id ON group_user_relations(user_id);
CREATE INDEX idx_group_user_relations_role_id ON group_user_relations(role_id);

-- Group service provider relations
CREATE INDEX idx_group_service_provider_relations_group_id ON group_service_provider_relations(group_id);
CREATE INDEX idx_group_service_provider_relations_service_provider_id ON group_service_provider_relations(service_provider_id);

-- Service accounts
CREATE INDEX idx_service_accounts_service_provider_id ON service_accounts(service_provider_id);

-- Parent child relations
CREATE INDEX idx_parent_child_relations_parent_group_id ON parent_child_relations(parent_group_id);
CREATE INDEX idx_parent_child_relations_child_group_id ON parent_child_relations(child_group_id);

COMMIT;
