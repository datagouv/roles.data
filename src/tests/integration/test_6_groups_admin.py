from src.tests.helpers import (
    create_group,
    random_name,
    random_sub_pro_connect,
    random_user,
    verify_user,
)


def test_update_group(client):
    """Test updating a group's name."""
    # Update the group name
    new_group_data = create_group(client)
    admin_email = new_group_data["admin"]["email"]
    admin_sub = random_sub_pro_connect()

    new_name = random_name()
    responseNotVerified = client.put(
        f"/groups/{new_group_data["id"]}?acting_user_sub={admin_sub}&group_name={new_name}"
    )
    # sub is unknown, so the request should fail
    assert responseNotVerified.status_code == 404

    verify_user(client, admin_email, admin_sub)
    response = client.put(
        f"/groups/{new_group_data["id"]}?acting_user_sub={admin_sub}&group_name={new_name}"
    )
    assert response.status_code == 200

    updated_group = response.json()
    assert updated_group["id"] == new_group_data["id"]
    assert updated_group["name"] == new_name

    # Test non-existent group
    response = client.put(
        f"/groups/999999?acting_user_sub={admin_sub}&group_name={new_name}"
    )
    assert response.status_code == 404

    # revert the group name
    response = client.put(
        f"/groups/{new_group_data['id']}?acting_user_sub={admin_sub}&group_name={new_group_data['name']}"
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
    user_data = user_response.json()

    random_sub = random_sub_pro_connect()
    verify_user(client, user_data["email"], random_sub)

    # Attempt to update the group with the non-admin user
    new_name = random_name()
    response = client.put(
        f"/groups/{new_group_data["id"]}?acting_user_sub={random_sub}&group_name={new_name}"
    )

    assert response.status_code == 403


def test_add_user_to_group_and_update_roles(client):
    """Test adding a user to a group."""
    # Create a user
    new_group_data = create_group(client)
    admin_email = new_group_data["admin"]["email"]
    admin_sub = random_sub_pro_connect()

    user_data = random_user()

    user_response = client.post("/users", json=user_data)
    user_id = user_response.json()["id"]

    # Create a role or use an existing one
    roles_response = client.get("/roles/")
    role_1 = roles_response.json()[0]
    role_2 = roles_response.json()[1]

    responseNotVerified = client.post(
        f"/groups/{new_group_data["id"]}/users?acting_user_sub={admin_sub}",
        json={"email": user_data["email"], "role_id": role_1["id"]},
    )

    # sub is unknown, so the request should fail
    assert responseNotVerified.status_code == 404

    verify_user(client, admin_email, admin_sub)

    # Add user to group with role
    response = client.post(
        f"/groups/{new_group_data["id"]}/users?acting_user_sub={admin_sub}",
        json={"email": user_data["email"], "role_id": role_1["id"]},
    )

    assert response.status_code == 201

    # response contains the user in the group
    new_user_in_group = response.json()
    assert new_user_in_group["email"] == user_data["email"]
    assert new_user_in_group["role_id"] == role_1["id"]
    assert new_user_in_group["role_name"] == role_1["role_name"]
    assert new_user_in_group["is_admin"] is True

    # Cannot add the same user again
    response_add_user_again = client.post(
        f"/groups/{new_group_data["id"]}/users?acting_user_sub={admin_sub}",
        json={"email": user_data["email"], "role_id": role_1["id"]},
    )
    assert response_add_user_again.status_code == 403

    # Verify user is in the group
    group_details = client.get(f"/groups/{new_group_data["id"]}")
    group_users = group_details.json()["users"]
    find_user = next(user for user in group_users if user["id"] == user_id)
    assert find_user is not None
    assert find_user["role_name"] == role_1["role_name"]

    # Update user role in group
    client.patch(
        f"/groups/{new_group_data["id"]}/users/{user_id}?acting_user_sub={admin_sub}&role_id={role_2['id']}"
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
    admin_email = new_group_data["admin"]["email"]
    admin_sub = random_sub_pro_connect()

    user_data = random_user()
    create_user_response = client.post("/users/", json=user_data)
    user_id = create_user_response.json()["id"]

    roles_response = client.get("/roles/")
    role_id = roles_response.json()[0]["id"]

    responseNotVerified = client.patch(
        f"/groups/{new_group_data['id']}/users/{user_id}?acting_user_sub={admin_sub}&role_id={role_id}"
    )
    # sub is unknown, so the request should fail
    assert responseNotVerified.status_code == 404

    verify_user(client, admin_email, admin_sub)

    # change user role
    client.patch(
        f"/groups/{new_group_data['id']}/users/{user_id}?acting_user_sub={admin_sub}&role_id={role_id}"
    )

    # Now remove the user from the group
    response = client.delete(
        f"/groups/{new_group_data['id']}/users/{user_id}?acting_user_sub={admin_sub}"
    )
    assert response.status_code == 204

    # Verify user is not in the group
    group_details = client.get(f"/groups/{new_group_data['id']}")
    group_users = group_details.json()["users"]
    assert not any(user["id"] == user_id for user in group_users)


def test_cannot_remove_only_admin_from_group(client):
    """Test that we cannot remove the only admin user from a group."""
    # Create a group with an admin user
    new_group_data = create_group(client)
    admin_email = new_group_data["admin"]["email"]
    admin_sub = random_sub_pro_connect()

    # Verify the admin user
    verify_user(client, admin_email, admin_sub)

    get_admin_response = client.get("/users/search", params={"email": admin_email})
    admin_id = get_admin_response.json()["id"]

    # Attempt to remove the only admin from the group
    response_delete_only_admin = client.delete(
        f"/groups/{new_group_data['id']}/users/{admin_id}?acting_user_sub={admin_sub}"
    )
    assert response_delete_only_admin.status_code == 403

    response_change_only_admin_role = client.patch(
        f"/groups/{new_group_data["id"]}/users/{admin_id}?acting_user_sub={admin_sub}&role_id={2}"
    )
    assert response_change_only_admin_role.status_code == 403
