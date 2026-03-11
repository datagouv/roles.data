from src.config import settings
from src.tests.helpers import create_group, get_group, mock_session


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


def test_admin_group_page_can_update_group_name(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(",")[0]
    group = create_group(client, admin_email=admin_email)
    renamed_group = "Renamed Group"
    session = {
        "user_email": admin_email,
        "is_super_admin": True,
        "user_sub": "00000000-0000-4000-8000-000000000001",
    }

    with mock_session(session):
        response = client.get(f"/admin/groups/{group['id']}")

    assert response.status_code == 200
    assert "Êtes-vous sûr de vouloir modifier le nom de ce groupe ?" in response.text

    with mock_session(session):
        response = client.post(
            f"/admin/groups/{group['id']}/name",
            data={"group_name": renamed_group},
            follow_redirects=False,
        )

    assert response.status_code == 303
    assert response.headers["location"] == f"/admin/groups/{group['id']}"

    updated_group = get_group(client, group["id"])
    assert updated_group["name"] == renamed_group
