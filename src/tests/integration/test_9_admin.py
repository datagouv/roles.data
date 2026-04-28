from src.config import settings
from src.tests.helpers import create_group, get_group, mock_session


def test_admin_users_list_shows_group_tags(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(" ")[0]
    first_group = create_group(client, admin_email=admin_email)
    second_group = create_group(client, admin_email=admin_email)

    with mock_session(
        {"user_email": admin_email, "is_admin": True, "is_super_admin": True}
    ):
        response = client.get("/admin/users/")

    assert response.status_code == 200
    assert first_group["name"] in response.text
    assert second_group["name"] in response.text
    assert f'href="/admin/groups/{first_group["id"]}"' in response.text
    assert f'href="/admin/groups/{second_group["id"]}"' in response.text


def test_admin_group_page_can_update_group_name(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(" ")[0]
    group = create_group(client, admin_email=admin_email)
    renamed_group = "Renamed Group"
    session = {
        "user_email": admin_email,
        "is_admin": True,
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


def test_admin_groups_list_shows_organisation_name(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(" ")[0]
    group = create_group(client, admin_email=admin_email)
    session = {
        "user_email": admin_email,
        "is_admin": True,
        "is_super_admin": True,
    }

    with mock_session(session):
        response = client.get("/admin/groups/")

    assert response.status_code == 200
    assert "DINUM" in response.text
    assert group["organisation_siret"] in response.text
    assert group["name"] in response.text


def test_viewer_admin_can_see_groups_and_users_but_not_write_actions(client):
    viewer_email = settings.VIEWER_ADMIN_EMAILS.split(" ")[0]
    group = create_group(client, admin_email=viewer_email)
    session = {
        "user_email": viewer_email,
        "is_admin": True,
        "is_viewer_admin": True,
        "can_write_admin": False,
        "can_view_admin_service_providers": False,
    }

    with mock_session(session):
        groups_response = client.get("/admin/groups/")

    assert groups_response.status_code == 200
    assert group["name"] in groups_response.text
    assert "Fournisseurs de service" not in groups_response.text
    assert "Logs" in groups_response.text

    with mock_session(session):
        group_response = client.get(f"/admin/groups/{group['id']}")

    assert group_response.status_code == 200
    assert "Modifier le nom du groupe" not in group_response.text
    assert "Supprimer le groupe" not in group_response.text
    assert "Set admin" not in group_response.text
    assert "<h2>Logs</h2>" in group_response.text

    with mock_session(session):
        users_response = client.get("/admin/users/")

    assert users_response.status_code == 200
    assert viewer_email in users_response.text


def test_viewer_admin_cannot_access_restricted_pages_or_write_actions(client):
    viewer_email = settings.VIEWER_ADMIN_EMAILS.split(" ")[0]
    group = create_group(client, admin_email=viewer_email)
    session = {
        "user_email": viewer_email,
        "is_admin": True,
        "is_viewer_admin": True,
        "can_write_admin": False,
        "can_view_admin_service_providers": False,
        "user_sub": "00000000-0000-4000-8000-000000000002",
    }

    with mock_session(session):
        logs_response = client.get("/admin/logs/")

    assert logs_response.status_code == 200

    with mock_session(session):
        service_providers_response = client.get("/admin/service-providers/")

    assert service_providers_response.status_code == 403

    with mock_session(session):
        rename_response = client.post(
            f"/admin/groups/{group['id']}/name",
            data={"group_name": "Should not work"},
            follow_redirects=False,
        )

    assert rename_response.status_code == 403

    with mock_session(session):
        delete_user_response = client.delete("/admin/users/1", follow_redirects=False)

    assert delete_user_response.status_code == 403
