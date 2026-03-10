from src.config import settings
from src.tests.helpers import create_group, mock_session


def test_admin_users_list_shows_group_tags(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(",")[0]
    first_group = create_group(client, admin_email=admin_email)
    second_group = create_group(client, admin_email=admin_email)

    with mock_session({"user_email": admin_email, "is_super_admin": True}):
        response = client.get("/admin/users/")

    assert response.status_code == 200
    assert first_group["name"] in response.text
    assert second_group["name"] in response.text
    assert f'href="/admin/groups/{first_group["id"]}"' in response.text
    assert f'href="/admin/groups/{second_group["id"]}"' in response.text
