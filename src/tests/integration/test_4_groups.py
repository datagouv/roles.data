from src.tests.helpers import random_group, random_name, random_user

new_group_data = random_group()


def test_list_groups(client):
    """Test listing all groups."""
    response = client.get("/groups/")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert (
        next(
            (group for group in groups if group["name"] == new_group_data["name"]), None
        )
        is None
    )


def test_create_group(client):
    """Test creating a new group."""
    response = client.post("/groups/", json=new_group_data)
    assert response.status_code == 201
    group = response.json()
    assert group["name"] == new_group_data["name"]
    assert "id" in group
    new_group_data["id"] = group["id"]

    response = client.get("/groups/")
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) > 0
    assert (
        next(
            (group for group in groups if group["name"] == new_group_data["name"]), None
        )
        is not None
    )


def test_get_group_with_users(client):
    """Test retrieving a group with its users."""
    # Create a new group
    response = client.get(f"/groups/{new_group_data['id']}")
    assert response.status_code == 200
    group = response.json()
    assert group["name"] == new_group_data["name"]
    assert "users" in group  # Should include users array, even if empty
    assert (
        next(
            (
                user
                for user in group["users"]
                if user["email"] == new_group_data["admin_email"]
            ),
            None,
        )
        is not None
    )


def test_get_group_not_found(client):
    """Test retrieving a non-existent group."""
    # Test non-existent group
    response = client.get("/groups/999999")
    assert response.status_code == 404


def test_update_group(client):
    """Test updating a group's name."""
    # Update the group name
    new_name = random_name()
    response = client.put(f"/groups/{new_group_data["id"]}?group_name={new_name}")
    assert response.status_code == 200

    updated_group = response.json()
    assert updated_group["id"] == new_group_data["id"]
    assert updated_group["name"] == new_name

    # Test non-existent group
    response = client.put(f"/groups/999999?group_name={new_name}")
    assert response.status_code == 404

    # revert the group name
    response = client.put(
        f"/groups/{new_group_data['id']}?group_name={new_group_data['name']}"
    )
    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == new_group_data["name"]


def test_add_user_to_group_and_update_roles(client):
    """Test adding a user to a group."""
    # Create a user
    user_data = random_user()

    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]

    # Create a role or use an existing one
    roles_response = client.get("/roles/")
    role_1 = roles_response.json()[0]
    role_2 = roles_response.json()[1]

    # Add user to group with role
    response = client.put(
        f"/groups/{new_group_data["id"]}/users/{user_id}?role_id={role_1['id']}"
    )
    assert response.status_code == 201

    # Verify user is in the group
    group_details = client.get(f"/groups/{new_group_data["id"]}")
    group_users = group_details.json()["users"]
    find_user = next(user for user in group_users if user["id"] == user_id)
    assert find_user is not None
    assert find_user["role_name"] == role_1["role_name"]

    # Update user role in group
    client.patch(
        f"/groups/{new_group_data["id"]}/users/{user_id}?role_id={role_2['id']}"
    )

    # Verify user has new role in the group
    group_details = client.get(f"/groups/{new_group_data["id"]}")
    group_users = group_details.json()["users"]
    find_user = next(user for user in group_users if user["id"] == user_id)
    assert find_user is not None
    assert find_user["role_name"] == role_2["role_name"]


def test_remove_user_from_group(client):
    """Test removing a user from a group."""

    user_data = random_user()

    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]

    roles_response = client.get("/roles/")
    role_id = roles_response.json()[0]["id"]

    # Add user to group
    client.post(f"/groups/{new_group_data['id']}/users/{user_id}?role_id={role_id}")

    # Now remove the user from the group
    response = client.delete(f"/groups/{new_group_data['id']}/users/{user_id}")
    assert response.status_code == 204

    # Verify user is not in the group
    group_details = client.get(f"/groups/{new_group_data['id']}")
    group_users = group_details.json()["users"]
    assert not any(user["id"] == user_id for user in group_users)


def test_update_scopes(client):
    """Test granting access to a group."""
    # Update access with new scopes
    new_scopes = "read,write,delete"
    response = client.patch(
        f"/groups/{new_group_data["id"]}/scopes?scopes={new_scopes}"
    )
    assert response.status_code == 200

    # Verify access was updated
    response = client.get(f"/groups/{new_group_data["id"]}")
    assert response.status_code == 200
    group = response.json()
    assert group["scopes"] == new_scopes


# def test_grant_scopes():
#     # Create a group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     # Grant access with scopes
#     scopes = "read,write"
#     response = client.put(f"/groups/{group_id}/scopes?scopes={scopes}")
#     assert response.status_code == 200

#     # Verify access was granted
#     response = client.get(f"/groups/{group_id}")
#     assert response.status_code == 200
#     group = response.json()
#     print(group)
#     assert group["scopes"] == scopes  # Assuming the response includes scopes
