"""
Integration tests for resource server endpoints.

These tests verify that ProConnect resource server authentication works correctly
and that users can only access and modify their own groups.
"""

from unittest.mock import patch
from uuid import uuid4

import pytest

from src.constants import MAX_USERS_PER_BATCH
from src.repositories.users_in_group import UsersInGroupRepository
from src.tests.helpers import (
    create_group,
    get_group,
    random_user,
    resource_server_auth_headers,
)


def test_list_groups_for_user(client):
    """Test listing groups returns only user's groups via resource server endpoint."""
    # Create a user and group via standard endpoints
    user = random_user()

    # Create group with this user as admin
    group = create_group(client, admin_email=user["email"])

    # Call resource server endpoint with this user's credentials
    headers = resource_server_auth_headers(user["sub_pro_connect"], user["email"])
    response = client.get("/resource-server/groups/", headers=headers)

    assert response.status_code == 200
    groups = response.json()
    assert len(groups) > 0
    # Verify the group we created is in the list
    assert any(g["id"] == group["id"] for g in groups)


def test_list_groups_for_different_users(client):
    """Test that different users see different groups."""
    # Create two users with different groups
    user1 = random_user()
    user2 = random_user()

    # Create group for user1
    group1 = create_group(client, admin_email=user1["email"])

    # Create group for user2
    group2 = create_group(client, admin_email=user2["email"])

    # User1 should only see their group
    headers1 = resource_server_auth_headers(user1["sub_pro_connect"], user1["email"])
    response1 = client.get("/resource-server/groups/", headers=headers1)
    assert response1.status_code == 200
    groups1 = response1.json()
    group1_ids = [g["id"] for g in groups1]
    assert group1["id"] in group1_ids
    assert group2["id"] not in group1_ids

    # User2 should only see their group
    headers2 = resource_server_auth_headers(user2["sub_pro_connect"], user2["email"])
    response2 = client.get("/resource-server/groups/", headers=headers2)
    assert response2.status_code == 200
    groups2 = response2.json()
    group2_ids = [g["id"] for g in groups2]
    assert group2["id"] in group2_ids
    assert group1["id"] not in group2_ids


def test_update_group_name_as_admin(client):
    """Test that admin can update group name via resource server."""
    admin = random_user()

    # Create group with admin
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Update group name as admin
    new_name = "Updated Group Name"
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    response = client.put(
        f"/resource-server/groups/{group_id}",
        params={"group_name": new_name},
        headers=headers,
    )

    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == new_name

    # Verify the change persisted
    group_check = get_group(client, group_id)
    assert group_check["name"] == new_name


def test_update_group_name_unauthorized(client):
    """Test that non-admin cannot update group name."""
    admin = random_user()
    non_admin = random_user()

    # Create group with admin
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Try to update group name as non-admin (different user)
    new_name = "Unauthorized Update"
    headers = resource_server_auth_headers(
        non_admin["sub_pro_connect"], non_admin["email"]
    )
    response = client.put(
        f"/resource-server/groups/{group_id}",
        params={"group_name": new_name},
        headers=headers,
    )

    # user does not exist
    assert response.status_code == 404


def test_add_user_to_group_as_admin(client):
    """Test that admin can add users to their group."""
    admin = random_user()
    new_member = random_user()

    # Create group
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Add new user to group
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={
            "email": new_member["email"],
            "role_id": 2,
        },  # role_id=2 is usually "member"
        headers=headers,
    )

    assert response.status_code == 201
    user_in_group = response.json()
    assert user_in_group["email"] == new_member["email"]

    # Verify user was added to group
    group_check = get_group(client, group_id)
    assert any(u["email"] == new_member["email"] for u in group_check["users"])


@pytest.mark.parametrize("uppercase_email", [False, True])
def test_add_existing_user_to_group_returns_conflict(client, uppercase_email):
    admin = random_user()
    member = random_user()
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    url = f"/resource-server/groups/{group_id}/users"

    response = client.post(
        url,
        json={"email": member["email"], "role_id": 2},
        headers=headers,
    )
    assert response.status_code == 201
    member_id = response.json()["id"]
    users_before = get_group(client, group_id)["users"]

    duplicate_email = member["email"].upper() if uppercase_email else member["email"]
    response = client.post(
        url,
        json={"email": duplicate_email, "role_id": 1},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"User with ID {member_id} is already in group {group_id}"
    }
    assert get_group(client, group_id)["users"] == users_before


def test_add_user_to_group_unknown_role_does_not_create_user(client, user_exists):
    """Test that an unknown role fails before the user is created."""
    admin = random_user()
    new_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.post(
        f"/resource-server/groups/{group['id']}/users",
        json={"email": new_member["email"], "role_id": 999999},
        headers=headers,
    )

    assert response.status_code == 404
    assert not user_exists(new_member["email"])


def test_add_user_to_group_failure_rolls_back_user_creation(client, user_exists):
    """Test that a user is not left behind when adding it to the group fails."""
    admin = random_user()
    new_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    with (
        patch.object(
            UsersInGroupRepository, "add_users", side_effect=RuntimeError("DB error")
        ),
        pytest.raises(RuntimeError),
    ):
        client.post(
            f"/resource-server/groups/{group['id']}/users",
            json={"email": new_member["email"], "role_id": 2},
            headers=headers,
        )

    assert not user_exists(new_member["email"])
    assert not any(
        u["email"] == new_member["email"]
        for u in get_group(client, group["id"])["users"]
    )


def test_add_user_to_group_unauthorized(client):
    """Test that non-admin cannot add users to a group."""
    admin = random_user()
    new_member = random_user()
    new_member_2 = random_user()

    # create and add new_member to a group
    create_group(client, admin_email=new_member["email"])

    # Create group with admin
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Try to add user as non-admin
    headers = resource_server_auth_headers(
        new_member["sub_pro_connect"], new_member["email"]
    )

    # try to add user to a group it does not belong
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": new_member_2["email"], "role_id": 2},
        headers=headers,
    )

    assert response.status_code == 403


def test_add_users_to_group_as_admin(client):
    """Test that admin can add several users to their group at once."""
    admin = random_user()
    new_admin = random_user()
    new_member = random_user()

    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    response = client.post(
        f"/resource-server/groups/{group_id}/users/batch",
        json={
            "users": [
                {"email": new_admin["email"], "role_id": 1},
                {"email": new_member["email"], "role_id": 2},
            ]
        },
        headers=headers,
    )

    assert response.status_code == 201
    users_in_group = response.json()
    assert [u["email"] for u in users_in_group] == [
        new_admin["email"],
        new_member["email"],
    ]
    assert [u["role_id"] for u in users_in_group] == [1, 2]
    assert [u["is_admin"] for u in users_in_group] == [True, False]

    # Verify users were added to group
    group_users = get_group(client, group_id)["users"]
    assert any(
        u["email"] == new_admin["email"] and u["role_id"] == 1 for u in group_users
    )
    assert any(
        u["email"] == new_member["email"] and u["role_id"] == 2 for u in group_users
    )


@pytest.mark.parametrize("uppercase_email", [False, True])
def test_add_users_to_group_duplicated_emails(client, user_exists, uppercase_email):
    """Test that the same email twice in a request adds nobody."""
    admin = random_user()
    new_member = random_user()
    other_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    duplicate_email = (
        new_member["email"].upper() if uppercase_email else new_member["email"]
    )
    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={
            "users": [
                {"email": new_member["email"], "role_id": 2},
                {"email": other_member["email"], "role_id": 2},
                {"email": duplicate_email, "role_id": 1},
            ]
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": f"Duplicated emails in request: {new_member['email']}"
    }
    assert not user_exists(new_member["email"])
    assert not user_exists(other_member["email"])


def test_add_users_to_group_existing_member_returns_conflict(client, user_exists):
    """Test that a user already in the group makes the whole request fail."""
    admin = random_user()
    member = random_user()
    new_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member["email"], "role_id": 2},
        headers=headers,
    )
    assert response.status_code == 201
    member_id = response.json()["id"]
    users_before = get_group(client, group_id)["users"]

    response = client.post(
        f"/resource-server/groups/{group_id}/users/batch",
        json={
            "users": [
                {"email": new_member["email"], "role_id": 2},
                {"email": member["email"], "role_id": 2},
            ]
        },
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": f"Users with ID {member_id} are already in group {group_id}"
    }
    assert get_group(client, group_id)["users"] == users_before
    assert not user_exists(new_member["email"])


def test_add_users_to_group_unknown_role_does_not_create_users(client, user_exists):
    """Test that an unknown role fails before any user is created."""
    admin = random_user()
    new_member = random_user()
    other_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={
            "users": [
                {"email": new_member["email"], "role_id": 2},
                {"email": other_member["email"], "role_id": 999999},
            ]
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert not user_exists(new_member["email"])
    assert not user_exists(other_member["email"])


def test_add_users_to_group_failure_rolls_back_user_creation(client, user_exists):
    """Test that no user is left behind when adding them to the group fails."""
    admin = random_user()
    new_member = random_user()
    other_member = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    with (
        patch.object(
            UsersInGroupRepository, "add_users", side_effect=RuntimeError("DB error")
        ),
        pytest.raises(RuntimeError),
    ):
        client.post(
            f"/resource-server/groups/{group['id']}/users/batch",
            json={
                "users": [
                    {"email": new_member["email"], "role_id": 2},
                    {"email": other_member["email"], "role_id": 2},
                ]
            },
            headers=headers,
        )

    assert not user_exists(new_member["email"])
    assert not user_exists(other_member["email"])


def test_add_users_to_group_empty_list(client):
    """Test that an empty list of users is rejected."""
    admin = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={"users": []},
        headers=headers,
    )

    assert response.status_code == 422


def test_add_users_to_group_unauthorized(client):
    """Test that non-admin cannot add users to a group."""
    admin = random_user()
    member = random_user()
    new_member = random_user()

    # create and add member to a group so that the user exists
    create_group(client, admin_email=member["email"])

    group = create_group(client, admin_email=admin["email"])

    headers = resource_server_auth_headers(member["sub_pro_connect"], member["email"])
    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={"users": [{"email": new_member["email"], "role_id": 2}]},
        headers=headers,
    )

    assert response.status_code == 403


def test_update_user_role_as_admin(client):
    """Test that admin can update user roles in their group."""
    admin = random_user()

    member = random_user()

    # Create group with admin and member
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Add member to group
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member["email"], "role_id": 2},  # role_id=2 is member
        headers=headers,
    )
    assert response.status_code == 201

    # Get the member's user_id from the response
    member_data = response.json()
    member_id = member_data["id"]

    # Update member's role to admin (role_id=1)
    response = client.patch(
        f"/resource-server/groups/{group_id}/users/{member_id}",
        params={"role_id": 1},
        headers=headers,
    )

    assert response.status_code == 200

    # Verify role was updated
    group_check = get_group(client, group_id)
    member_in_group = next(
        u for u in group_check["users"] if u["email"] == member["email"]
    )
    assert member_in_group["role_id"] == 1


def test_update_user_role_unauthorized(client):
    """Test that non-admin cannot update user roles."""
    admin = random_user()
    member = random_user()

    # Create group and add member
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    admin_headers = resource_server_auth_headers(
        admin["sub_pro_connect"], admin["email"]
    )
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member["email"], "role_id": 2},
        headers=admin_headers,
    )
    assert response.status_code == 201

    # Get the member's user_id from the response
    member_data = response.json()
    member_id = member_data["id"]

    # Try to update role as non-admin
    non_admin_headers = resource_server_auth_headers(
        member["sub_pro_connect"], member["email"]
    )
    response = client.patch(
        f"/resource-server/groups/{group_id}/users/{member_id}",
        params={"role_id": 1},
        headers=non_admin_headers,
    )

    assert response.status_code == 403


def test_remove_user_from_group_as_admin(client):
    """Test that admin can remove users from their group."""
    admin = random_user()
    member = random_user()

    # Create group with admin and member
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    # Add member
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member["email"], "role_id": 2},
        headers=headers,
    )
    assert response.status_code == 201

    # Get member's user_id from the response
    member_data = response.json()
    member_id = member_data["id"]

    # Remove member from group
    response = client.delete(
        f"/resource-server/groups/{group_id}/users/{member_id}",
        headers=headers,
    )

    assert response.status_code == 204

    # Verify member was removed
    group_check = get_group(client, group_id)
    assert not any(u["email"] == member["email"] for u in group_check["users"])


def test_remove_user_from_group_unauthorized(client):
    """Test that non-admin cannot remove users from a group."""
    admin = random_user()
    member = random_user()
    member_2 = random_user()

    # create group
    group = create_group(client, admin_email=admin["email"])
    group_id = group["id"]

    admin_headers = resource_server_auth_headers(
        admin["sub_pro_connect"], admin["email"]
    )
    # add user to group
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member["email"], "role_id": 2},
        headers=admin_headers,
    )
    assert response.status_code == 201

    # Try to add another user but without admin rights
    non_admin_headers = resource_server_auth_headers(
        member["sub_pro_connect"], member["email"]
    )
    response = client.post(
        f"/resource-server/groups/{group_id}/users",
        json={"email": member_2["email"], "role_id": 2},
        headers=non_admin_headers,
    )

    assert response.status_code == 403


def test_resource_server_without_bearer_token(client):
    """Test that resource server endpoints require authentication."""
    # Try to access resource server endpoint without bearer token
    response = client.get("/resource-server/groups/")

    # Should fail with 403 Forbidden (missing bearer token)
    assert response.status_code == 403


def test_list_organization_groups(client):
    """Test listing groups by organization SIRET."""
    from unittest.mock import AsyncMock, patch

    from src.tests.helpers import DINUM_SIRET

    # Create users with different groups
    admin1 = random_user()
    admin2 = random_user()

    # Create groups with DINUM_SIRET (default SIRET used by create_group)
    group1 = create_group(client, admin_email=admin1["email"])
    group2 = create_group(client, admin_email=admin2["email"])

    # Mock pro_connect_provider.userinfo to return DINUM_SIRET
    mock_userinfo = AsyncMock(return_value={"siret": DINUM_SIRET})

    with patch(
        "src.dependencies.auth.pro_connect_resource_server.pro_connect_provider.userinfo",
        mock_userinfo,
    ):
        # Call organization groups endpoint
        headers = resource_server_auth_headers(
            admin1["sub_pro_connect"], admin1["email"]
        )
        response = client.get("/resource-server/organizations/groups", headers=headers)

        assert response.status_code == 200
        groups = response.json()

        # Should return all groups for the organization
        assert len(groups) >= 2

        # Verify our groups are in the response
        group_ids = [g["id"] for g in groups]
        assert group1["id"] in group_ids
        assert group2["id"] in group_ids

        # Verify response structure includes admin_emails
        for group in groups:
            assert "id" in group
            assert "name" in group
            assert "organisation_siret" in group
            assert "scopes" in group
            assert "admin_emails" in group
            assert isinstance(group["admin_emails"], list)

        # Verify admin emails are present in the groups
        group1_data = next(g for g in groups if g["id"] == group1["id"])
        assert admin1["email"] in group1_data["admin_emails"]

        group2_data = next(g for g in groups if g["id"] == group2["id"])
        assert admin2["email"] in group2_data["admin_emails"]


def test_list_organization_groups_different_siret(client):
    """Test that different SIRETs return different groups."""
    from unittest.mock import AsyncMock, patch

    # Create a group with DINUM_SIRET
    admin1 = random_user()
    group1 = create_group(client, admin_email=admin1["email"])

    # Mock userinfo to return a different SIRET
    different_siret = "55208779803527"  # Valid but different SIRET
    mock_userinfo = AsyncMock(return_value={"siret": different_siret})

    with patch(
        "src.dependencies.auth.pro_connect_resource_server.pro_connect_provider.userinfo",
        mock_userinfo,
    ):
        headers = resource_server_auth_headers(
            admin1["sub_pro_connect"], admin1["email"]
        )
        response = client.get("/resource-server/organizations/groups", headers=headers)

        assert response.status_code == 200
        groups = response.json()

        # Should not return groups from DINUM_SIRET
        group_ids = [g["id"] for g in groups]
        assert group1["id"] not in group_ids


def test_add_users_to_group_above_batch_limit(client):
    """Test that a batch holding more than the allowed number of users is rejected."""
    admin = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={
            "users": [
                {"email": f"member_{i}@beta.gouv.fr", "role_id": 2}
                for i in range(MAX_USERS_PER_BATCH + 1)
            ]
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_list_groups_carries_admins_and_the_asking_user_role(client):
    """Test that a listed group carries its admins and the role of the caller."""
    admin = random_user()
    group = create_group(client, admin_email=admin["email"], member_count=60)
    member_email = group["members"][0]["email"]

    admin_headers = resource_server_auth_headers(
        admin["sub_pro_connect"], admin["email"]
    )
    response = client.get("/resource-server/groups/", headers=admin_headers)

    assert response.status_code == 200
    listed_group = next(g for g in response.json() if g["id"] == group["id"])
    # A listing never carries the users of a group, however many there are
    assert "users" not in listed_group
    assert [a["email"] for a in listed_group["admins"]] == [admin["email"]]
    assert listed_group["current_user_role"]["role_name"] == "administrateur"
    assert listed_group["current_user_role"]["is_admin"] is True

    member_headers = resource_server_auth_headers(uuid4(), member_email)
    response = client.get("/resource-server/groups/", headers=member_headers)

    assert response.status_code == 200
    listed_group = next(g for g in response.json() if g["id"] == group["id"])
    # A member sees who to ask for a role change, and their own role
    assert [a["email"] for a in listed_group["admins"]] == [admin["email"]]
    assert listed_group["current_user_role"]["role_name"] == "utilisateur"
    assert listed_group["current_user_role"]["is_admin"] is False


def test_list_groups_carries_at_most_three_admins(client):
    """Test that a listed group never carries more than three of its admins."""
    admin = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    new_admins = [random_user() for _ in range(4)]
    response = client.post(
        f"/resource-server/groups/{group['id']}/users/batch",
        json={"users": [{"email": a["email"], "role_id": 1} for a in new_admins]},
        headers=headers,
    )
    assert response.status_code == 201

    response = client.get("/resource-server/groups/", headers=headers)

    assert response.status_code == 200
    listed_group = next(g for g in response.json() if g["id"] == group["id"])
    assert len(listed_group["admins"]) == 3
    # The oldest admins first, the group's own admin among them
    assert listed_group["admins"][0]["email"] == admin["email"]


def test_get_group_users_are_paginated(client):
    """Test that a group's users come back one page at a time, 50 by default."""
    admin = random_user()
    # 60 members and the admin
    group = create_group(client, admin_email=admin["email"], member_count=60)
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])
    url = f"/resource-server/groups/{group['id']}"

    response = client.get(url, headers=headers)

    assert response.status_code == 200
    first_page = response.json()
    assert len(first_page["users"]) == 50
    assert first_page["users_pagination"] == {
        "page": 1,
        "size": 50,
        "total": 61,
        "total_pages": 2,
    }

    response = client.get(url, params={"usersPage": 2}, headers=headers)

    assert response.status_code == 200
    second_page = response.json()
    assert len(second_page["users"]) == 11
    assert second_page["users_pagination"]["page"] == 2

    # Every user of the group is reachable, and none is served twice
    page_user_ids = [user["id"] for user in first_page["users"] + second_page["users"]]
    assert len(set(page_user_ids)) == 61


def test_get_group_users_page_size(client):
    """Test that the caller can choose how many users a page holds."""
    admin = random_user()
    # 3 members and the admin
    group = create_group(client, admin_email=admin["email"], member_count=3)
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.get(
        f"/resource-server/groups/{group['id']}",
        params={"usersSize": 2, "usersPage": 2},
        headers=headers,
    )

    assert response.status_code == 200
    page = response.json()
    assert len(page["users"]) == 2
    assert page["users_pagination"] == {
        "page": 2,
        "size": 2,
        "total": 4,
        "total_pages": 2,
    }


@pytest.mark.parametrize(
    "params", [{"usersPage": 0}, {"usersSize": 0}, {"usersSize": 201}]
)
def test_get_group_rejects_invalid_pagination(client, params):
    """Test that out of range pagination parameters are rejected."""
    admin = random_user()
    group = create_group(client, admin_email=admin["email"])
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    response = client.get(
        f"/resource-server/groups/{group['id']}", params=params, headers=headers
    )

    assert response.status_code == 422


def test_get_group_as_member_and_as_stranger(client):
    """Test that only the users of a group can read it."""
    admin = random_user()
    stranger = random_user()
    group = create_group(client, admin_email=admin["email"])
    member_email = group["members"][0]["email"]

    member_headers = resource_server_auth_headers(uuid4(), member_email)
    response = client.get(
        f"/resource-server/groups/{group['id']}", headers=member_headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == group["name"]

    # The stranger has a group of their own, so they are a known user
    create_group(client, admin_email=stranger["email"])
    stranger_headers = resource_server_auth_headers(
        stranger["sub_pro_connect"], stranger["email"]
    )
    response = client.get(
        f"/resource-server/groups/{group['id']}", headers=stranger_headers
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "User is not member of the group."}


def test_get_group_not_found(client):
    """Test reading a group that does not exist."""
    user = random_user()
    create_group(client, admin_email=user["email"])
    headers = resource_server_auth_headers(user["sub_pro_connect"], user["email"])

    response = client.get("/resource-server/groups/999999", headers=headers)

    assert response.status_code == 404


def test_group_membership_is_checked_beyond_the_first_page_of_users(client):
    """Test that membership checks see the whole group, not just a page of users."""
    admin = random_user()
    # 60 members and the admin
    group = create_group(client, admin_email=admin["email"], member_count=60)
    headers = resource_server_auth_headers(admin["sub_pro_connect"], admin["email"])

    second_page = client.get(
        f"/resource-server/groups/{group['id']}",
        params={"usersPage": 2},
        headers=headers,
    ).json()["users"]
    user_beyond_first_page = second_page[-1]

    # Adding them again is a conflict, although they are not on the first page
    response = client.post(
        f"/resource-server/groups/{group['id']}/users",
        json={"email": user_beyond_first_page["email"], "role_id": 2},
        headers=headers,
    )
    assert response.status_code == 409

    # And their role can still be updated
    response = client.patch(
        f"/resource-server/groups/{group['id']}/users/{user_beyond_first_page['id']}",
        params={"role_id": 1},
        headers=headers,
    )
    assert response.status_code == 200
