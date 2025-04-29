INSERT INTO d_roles.roles (id, role_name, is_admin) VALUES
(1, 'admin', true),
(2, 'user', false) ON CONFLICT DO NOTHING;
