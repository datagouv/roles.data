CREATE SCHEMA d_roles;
-- Create the database tables

-- Organizations table
CREATE TABLE  IF NOT EXISTS d_roles.organisations (
    id SERIAL PRIMARY KEY,
    siren CHAR(9) NOT NULL CHECK (siren ~ '^[0-9]{9}$'),
    name VARCHAR(255) NOT NULL
);

-- Teams table
CREATE TABLE  IF NOT EXISTS d_roles.team (
    id SERIAL PRIMARY KEY,
    orga_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    CONSTRAINT fk_team_orga FOREIGN KEY (orga_id) REFERENCES d_roles.organisations (id) ON DELETE CASCADE
);

-- Parent-Child relationship table
CREATE TABLE IF NOT EXISTS d_roles.parent_child (
    parent_team_id INTEGER NOT NULL,
    child_team_id INTEGER NOT NULL,
    inherit_scopes BOOLEAN NOT NULL DEFAULT false,
    PRIMARY KEY (parent_team_id, child_team_id),
    CONSTRAINT fk_parent_child_parent FOREIGN KEY (parent_team_id) REFERENCES d_roles.team (id) ON DELETE CASCADE,
    CONSTRAINT fk_parent_child_child FOREIGN KEY (child_team_id) REFERENCES d_roles.team (id) ON DELETE CASCADE
);

-- Members table
CREATE TABLE IF NOT EXISTS d_roles.members (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    sub_pro_connect VARCHAR(255),
    is_email_confirmed BOOLEAN NOT NULL DEFAULT false
);

-- Roles table
CREATE TABLE IF NOT EXISTS d_roles.roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE,
    is_admin BOOLEAN NOT NULL DEFAULT false
);

-- Team Members
CREATE TABLE IF NOT EXISTS d_roles.team_member_relation (
    team_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (team_id, member_id, role_id),
    CONSTRAINT team_member_fk_relation_team FOREIGN KEY (team_id) REFERENCES d_roles.team (id) ON DELETE CASCADE,
    CONSTRAINT team_member_fk_relation_member FOREIGN KEY (member_id) REFERENCES d_roles.members (id) ON DELETE CASCADE,
    CONSTRAINT team_member_fk_relation_role FOREIGN KEY (role_id) REFERENCES d_roles.roles (id) ON DELETE CASCADE
);

-- Service Providers table
CREATE TABLE  IF NOT EXISTS d_roles.service_provider (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Service Accounts table
CREATE TABLE  IF NOT EXISTS d_roles.service_account (
    id SERIAL PRIMARY KEY,
    service_provider_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Scopes table
CREATE TABLE  IF NOT EXISTS d_roles.team_service_provider_relation (
    service_provider_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    PRIMARY KEY (service_provider_id, team_id),
    scopes TEXT NOT NULL,
    CONSTRAINT fk_scopes_team FOREIGN KEY (team_id) REFERENCES d_roles.team (id) ON DELETE CASCADE,
    CONSTRAINT fk_scopes_project FOREIGN KEY (service_provider_id) REFERENCES d_roles.service_provider (id) ON DELETE CASCADE
);

-- Service account to service provider relationship
CREATE TABLE  IF NOT EXISTS d_roles.service_account_provider (
    service_account_id INTEGER NOT NULL,
    service_provider_id INTEGER NOT NULL,
    token TEXT NOT NULL,
    PRIMARY KEY (service_account_id, service_provider_id),
    CONSTRAINT fk_sa_provider_account FOREIGN KEY (service_account_id) REFERENCES d_roles.service_account (id) ON DELETE CASCADE,
    CONSTRAINT fk_sa_provider_project FOREIGN KEY (service_provider_id) REFERENCES d_roles.service_provider (id) ON DELETE CASCADE
);
