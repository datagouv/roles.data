from src.tests.helpers import random_group, random_name, random_user


def create_group(client):
    """Create a group for testing."""
    new_group_data = random_group()
    response = client.post("/groups/", json=new_group_data)
    assert response.status_code == 201
    group = response.json()
    assert group["name"] == new_group_data["name"]
    new_group_data["id"] = group["id"]
    return new_group_data


def test_list_groups(client):
    """Test listing all groups."""
    response = client.get("/groups/")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert (
        next((group for group in groups if group["name"] == "stack technique"), None)
        is not None
    )


def test_create_group(client):
    """Test creating a new group."""
    new_group = create_group(client)

    response = client.get(f"/groups/{new_group['id']}")
    assert response.status_code == 200
    group = response.json()
    assert "id" in group
    assert group["name"] == new_group["name"]
    assert group["organisation_siren"] == new_group["organisation_siren"]
    assert group["scopes"] == new_group["scopes"]
    assert group["contract"] == new_group["contract"]
    assert group["users"][0]["email"] == new_group["admin_email"]


def test_get_group_with_users(client):
    """Test retrieving a group with its users."""
    # Create a new group
    new_group_data = create_group(client)

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


def test_search_group_by_user(client):
    """Test searching groups by user email"""
    # Create a new group
    new_group_data = create_group(client)

    response = client.get(
        "/groups/search", params={"email": new_group_data["admin_email"]}
    )
    assert response.status_code == 200
    group = response.json()
    assert isinstance(group, list)
    assert len(group) == 1
    assert group[0]["name"] == new_group_data["name"]
    assert group[0]["organisation_siren"] == new_group_data["organisation_siren"]
    assert group[0]["scopes"] == new_group_data["scopes"]
    assert group[0]["contract"] == new_group_data["contract"]
    assert group[0]["users"][0]["email"] == new_group_data["admin_email"]

    # Test non-existent user
    response404 = client.get("/groups/search", params={"email": "hey@test.fr"})
    assert response404.status_code == 404

    # Test non-existent group
    responseEmpty = client.get(
        "/groups/search", params={"email": "user-not-in-group@beta.gouv.fr"}
    )
    assert responseEmpty.status_code == 200
    group = responseEmpty.json()
    assert isinstance(group, list)
    assert len(group) == 0


def test_get_group_not_found(client):
    """Test retrieving a non-existent group."""
    # Test non-existent group
    response = client.get("/groups/999999")
    assert response.status_code == 404


def test_update_group(client):
    """Test updating a group's name."""
    # Update the group name
    new_group_data = create_group(client)

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
    new_group_data = create_group(client)

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
    new_group_data = create_group(client)

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
    new_group_data = create_group(client)

    new_scopes = "read,write,delete"
    new_contract = "datapass_48"
    response = client.patch(
        f"/groups/{new_group_data["id"]}/scopes?scopes={new_scopes}&contract={new_contract}"
    )
    assert response.status_code == 200

    # Verify access was updated
    response = client.get(f"/groups/{new_group_data["id"]}")
    assert response.status_code == 200
    group = response.json()
    assert group["scopes"] == new_scopes
    assert group["contract"] == new_contract
