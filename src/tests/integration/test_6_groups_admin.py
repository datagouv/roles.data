from src.tests.helpers import create_group, random_name, random_user


def get_admin_id(client, admin_email: str):
    """Get the ID of the admin user."""
    admin_response = client.get("/users/search", params={"email": admin_email})
    return admin_response.json()["id"]


def test_update_group(client):
    """Test updating a group's name."""
    # Update the group name
    new_group_data = create_group(client)
    admin_id = get_admin_id(client, new_group_data["admin_email"])

    print(f"Admin ID: {admin_id}")

    new_name = random_name()
    response = client.put(
        f"/groups/{new_group_data["id"]}?admin_id={admin_id}&group_name={new_name}"
    )
    assert response.status_code == 200

    updated_group = response.json()
    assert updated_group["id"] == new_group_data["id"]
    assert updated_group["name"] == new_name

    # Test non-existent group
    response = client.put(f"/groups/999999?admin_id={admin_id}&group_name={new_name}")
    assert response.status_code == 404

    # revert the group name
    response = client.put(
        f"/groups/{new_group_data['id']}?admin_id={admin_id}&group_name={new_group_data['name']}"
    )
    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == new_group_data["name"]


def test_user_not_admin(client):
    """Test that a non-admin user cannot update a group."""
    # Create a group
    new_group_data = create_group(client)

    # Create a non-admin user
    user_data = random_user()
    user_response = client.post("/users", json=user_data)
    user_id = user_response.json()["id"]

    # Attempt to update the group with the non-admin user
    new_name = random_name()
    response = client.put(
        f"/groups/{new_group_data["id"]}?admin_id={user_id}&group_name={new_name}"
    )
    assert response.status_code == 403


def test_add_user_to_group_and_update_roles(client):
    """Test adding a user to a group."""
    # Create a user
    new_group_data = create_group(client)
    admin_id = get_admin_id(client, new_group_data["admin_email"])

    user_data = random_user()

    user_response = client.post("/users", json=user_data)
    user_id = user_response.json()["id"]

    # Create a role or use an existing one
    roles_response = client.get("/roles/")
    role_1 = roles_response.json()[0]
    role_2 = roles_response.json()[1]

    # Add user to group with role
    response = client.put(
        f"/groups/{new_group_data["id"]}/users/{user_id}?admin_id={admin_id}&role_id={role_1['id']}"
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
        f"/groups/{new_group_data["id"]}/users/{user_id}?admin_id={admin_id}&role_id={role_2['id']}"
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
    admin_id = get_admin_id(client, new_group_data["admin_email"])

    user_data = random_user()

    user_response = client.post("/users/", json=user_data)
    user_id = user_response.json()["id"]

    roles_response = client.get("/roles/")
    role_id = roles_response.json()[0]["id"]

    # Add user to group
    client.post(
        f"/groups/{new_group_data['id']}/users/{user_id}?admin_id={admin_id}&role_id={role_id}"
    )

    # Now remove the user from the group
    response = client.delete(
        f"/groups/{new_group_data['id']}/users/{user_id}?admin_id={admin_id}"
    )
    assert response.status_code == 204

    # Verify user is not in the group
    group_details = client.get(f"/groups/{new_group_data['id']}")
    group_users = group_details.json()["users"]
    assert not any(user["id"] == user_id for user in group_users)
