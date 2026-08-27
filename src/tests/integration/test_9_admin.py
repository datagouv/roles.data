from datetime import datetime, timezone
from html import unescape
import re
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlsplit

import pytest

from src.config import settings
from src.repositories.admin.admin_read_repository import AdminReadRepository
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


def test_admin_group_page_can_add_update_and_remove_group_users(client):
    admin_email = settings.SUPER_ADMIN_EMAILS.split(" ")[0]
    group = create_group(client, admin_email=admin_email)
    new_user_email = "  New.Group.Member@Beta.Gouv.Fr  "
    normalized_new_user_email = "new.group.member@beta.gouv.fr"
    session = {
        "user_email": admin_email,
        "is_admin": True,
        "is_super_admin": True,
        "user_sub": "00000000-0000-4000-8000-000000000003",
    }

    with mock_session(session):
        add_response = client.post(
            f"/admin/groups/{group['id']}/users",
            data={"user_email": new_user_email, "role_id": 2},
            follow_redirects=False,
        )

    assert add_response.status_code == 303

    group_after_add = get_group(client, group["id"])
    added_user = next(
        user
        for user in group_after_add["users"]
        if user["email"] == normalized_new_user_email
    )
    assert added_user["role_name"] == "utilisateur"

    with mock_session(session):
        update_response = client.post(
            f"/admin/groups/{group['id']}/users/{added_user['id']}/role",
            data={"role_id": 1},
            follow_redirects=False,
        )

    assert update_response.status_code == 303

    group_after_update = get_group(client, group["id"])
    updated_user = next(
        user for user in group_after_update["users"] if user["id"] == added_user["id"]
    )
    assert updated_user["role_name"] == "administrateur"

    with mock_session(session):
        remove_response = client.post(
            f"/admin/groups/{group['id']}/users/{added_user['id']}/remove",
            follow_redirects=False,
        )

    assert remove_response.status_code == 303

    group_after_remove = get_group(client, group["id"])
    assert all(user["id"] != added_user["id"] for user in group_after_remove["users"])


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


@pytest.fixture(params=["groups", "users"])
def admin_list(request, monkeypatch):
    """Exercise the routes, service and templates with deterministic repository rows."""
    records = [
        {
            "id": 2,
            "name": "Équipe Été & Données + 100%",
            "email": "Équipe.Été+100%@example.com",
            "user_count": 2,
            "created_at": datetime(2026, 2, 1, 12, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 3, 1, 11, tzinfo=timezone.utc),
        },
        {
            "id": 10,
            "name": "alpha",
            "email": "alpha@example.com",
            "user_count": 10,
            "created_at": datetime(2026, 2, 1, 13, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 2, 28, tzinfo=timezone.utc),
        },
        {
            "id": 21,
            "name": "zulu",
            "email": "zulu@example.com",
            "user_count": 1,
            "created_at": datetime(2026, 1, 31, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 3, 1, 10, tzinfo=timezone.utc),
        },
    ]
    for record in records:
        record.update(organisation_name="DINUM", organisation_siret="13002526500013")

    monkeypatch.setattr(
        AdminReadRepository, f"read_{request.param}", AsyncMock(return_value=records)
    )
    group_lookup = AsyncMock(return_value={2: [{"id": 50, "name": "Groupe associé"}]})
    monkeypatch.setattr(AdminReadRepository, "read_user_groups_by_ids", group_lookup)

    admin_email = settings.SUPER_ADMIN_EMAILS.split(" ")[0]
    with mock_session(
        {"user_email": admin_email, "is_admin": True, "is_super_admin": True}
    ):
        yield request.param, group_lookup


@pytest.mark.parametrize(
    ("search", "expected_ids"),
    [
        ("EQUIPE", [2]),
        ("e\u0301QuiPe", [2]),
        ("  été  ", [2]),
        ("ÁLPHA", [10]),
        ("10", [2, 10]),
        ("21", [21]),
        ("1", [2, 10, 21]),
        ("%", [2]),
        ("_", []),
        ("no-match", []),
        ("", [2, 10, 21]),
        ("   ", [2, 10, 21]),
    ],
)
def test_admin_lists_search(client, admin_list, search, expected_ids):
    resource, group_lookup = admin_list
    response = client.get(f"/admin/{resource}/", params={"search": search})

    assert response.status_code == 200
    assert [row["id"] for row in response.context[resource]] == expected_ids
    assert response.context["search"] == search
    if not expected_ids:
        assert "Aucun résultats" in response.text
        assert 'type="search"' in response.text
    if resource == "users":
        group_lookup.assert_awaited_once_with(expected_ids)
        if 2 in expected_ids:
            assert 'href="/admin/groups/50"' in response.text


@pytest.mark.parametrize("sort_direction", ["asc", "desc"])
@pytest.mark.parametrize(
    ("sort_by", "expected_ids"),
    [
        ("id", [2, 10, 21]),
        ("text", [10, 2, 21]),
        ("created_at", [21, 2, 10]),
        ("updated_at", [10, 21, 2]),
    ],
)
def test_admin_lists_sort_columns(
    client, admin_list, sort_by, sort_direction, expected_ids
):
    resource, _ = admin_list
    if sort_by == "text":
        sort_by = "name" if resource == "groups" else "email"
    if sort_direction == "desc":
        expected_ids = list(reversed(expected_ids))

    response = client.get(
        f"/admin/{resource}/",
        params={"sortBy": sort_by, "sortDirection": sort_direction},
    )

    assert response.status_code == 200
    assert [row["id"] for row in response.context[resource]] == expected_ids
    aria_sort = "ascending" if sort_direction == "asc" else "descending"
    assert response.text.count(f'aria-sort="{aria_sort}"') == 1


@pytest.mark.parametrize("admin_list", ["groups"], indirect=True)
@pytest.mark.parametrize(
    ("sort_direction", "expected_ids"),
    [("asc", [21, 2, 10]), ("desc", [10, 2, 21])],
)
def test_admin_groups_sort_user_counts(
    client, admin_list, sort_direction, expected_ids
):
    response = client.get(
        "/admin/groups/",
        params={"sortBy": "user_count", "sortDirection": sort_direction},
    )

    assert response.status_code == 200
    assert [row["id"] for row in response.context["groups"]] == expected_ids


def test_admin_lists_search_form_and_sort_links_preserve_query(client, admin_list):
    resource, _ = admin_list
    search = (
        "Équipe Été & Données + 100%" if resource == "groups" else "Équipe.Été+100%"
    )
    response = client.get(
        f"/admin/{resource}/",
        params={"search": search, "sortBy": "id", "sortDirection": "asc"},
    )

    assert response.status_code == 200
    assert f'<form method="get" action="/admin/{resource}/"' in response.text
    assert 'type="search" id="list-search" name="search"' in response.text
    assert f'value="{search}"' in unescape(response.text)
    assert '<button class="fr-btn" type="submit">Rechercher</button>' in response.text
    assert 'name="sortBy" value="id"' in response.text
    assert 'name="sortDirection" value="asc"' in response.text

    links = [
        unescape(link)
        for link in re.findall(r'<a href="([^"]+)"\s+aria-label=', response.text)
    ]
    expected_columns = {"id", "created_at", "updated_at"}
    expected_columns.update(
        {"name", "user_count"} if resource == "groups" else {"email"}
    )
    assert len(links) == len(expected_columns)
    assert {
        parse_qs(urlsplit(link).query)["sortBy"][0] for link in links
    } == expected_columns

    for link in links:
        query = parse_qs(urlsplit(link).query)
        assert query["search"] == [search]
        expected_direction = "desc" if query["sortBy"] == ["id"] else "asc"
        assert query["sortDirection"] == [expected_direction]
        sorted_response = client.get(link)
        assert sorted_response.status_code == 200
        assert [row["id"] for row in sorted_response.context[resource]] == [2]
        assert f'name="sortBy" value="{query["sortBy"][0]}"' in sorted_response.text
        assert (
            f'name="sortDirection" value="{expected_direction}"' in sorted_response.text
        )
        if query["sortBy"] == ["id"]:
            assert 'aria-sort="descending"' in sorted_response.text
            assert "sortDirection=asc" in unescape(sorted_response.text)


@pytest.mark.parametrize(
    "params",
    [
        {"sortBy": "unknown"},
        {"sortBy": "id; DROP TABLE users"},
        {"sortDirection": "invalid"},
    ],
)
def test_admin_lists_reject_invalid_sort_parameters(client, admin_list, params):
    resource, _ = admin_list
    response = client.get(f"/admin/{resource}/", params=params)

    assert response.status_code == 422


def test_admin_lists_escape_search_input(client, admin_list):
    resource, _ = admin_list
    search = '"><script>alert("search")</script>'
    response = client.get(f"/admin/{resource}/", params={"search": search})

    assert response.status_code == 200
    assert "<script>alert" not in response.text
    assert "&lt;script&gt;" in response.text
