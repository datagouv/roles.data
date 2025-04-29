INSERT INTO d_roles.roles (id, role_name, is_admin) VALUES
(1, 'admin', true),
(2, 'user', false) ON CONFLICT DO NOTHING;

INSERT INTO d_roles.users (email, sub_pro_connect, is_email_confirmed) VALUES
('user@yopmail.com', '', false) ON CONFLICT DO NOTHING;
