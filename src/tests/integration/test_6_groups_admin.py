from src.tests.helpers import (
    assert_email_sent,
    clear_mailhog_messages,
    create_group,
    get_user,
    random_name,
    random_sub_pro_connect,
    random_user,
)

# as we stub proconnect token there can be only one admin using resource_server routes
ADMIN_EMAIL = "admin@email.org"


def test_get_user_groups_and_user_verification(client):
    new_group_data = create_group(client, ADMIN_EMAIL)
    admin = get_user(client, new_group_data["admin"]["email"])
    assert admin["is_verified"] is False

    responseNotVerified = client.put(
        f"/resource_server/groups/{new_group_data['id']}?group_name=hey"
    )
    # sub not yet knwon user is not verified - request should fail
    assert responseNotVerified.status_code == 404

    user_groups_response = client.get(
        "/resource_server/groups/",
        params={"user_email": new_group_data["admin"]["email"]},
    )

    assert user_groups_response.status_code == 200
    print(user_groups_response.json())
    assert len(user_groups_response.json()) == 1
    admin = get_user(client, new_group_data["admin"]["email"])
    assert admin["is_verified"] is True


def test_update_group(client):
    """Test updating a group's name."""
    # Update the group name
    new_group_data = create_group(client, ADMIN_EMAIL)

    new_name = random_name()
    response = client.put(
        f"/resource_server/groups/{new_group_data['id']}?group_name={new_name}"
    )
    assert response.status_code == 200

    updated_group = response.json()
    assert updated_group["id"] == new_group_data["id"]
    assert updated_group["name"] == new_name

    # Test non-existent group
    response = client.put(f"/resource_server/groups/999999?group_name={new_name}")
    assert response.status_code == 404

    # revert the group name
    response = client.put(
        f"/resource_server/groups/{new_group_data['id']}?group_name={new_group_data['name']}"
    )
    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == new_group_data["name"]


# def test_user_not_admin(client):
#     """Test that a non-admin user cannot update a group."""
#     # Create a group

#     # TODO need to test on an existing group pre-seeded
#     assert response.status_code == 403


def test_add_user_to_group_and_update_roles(client):
    """Test adding a user to a group."""
    # Create a user
    new_group_data = create_group(client)

    user_data = random_user()

    user_response = client.post("/users", json=user_data)
    user_id = user_response.json()["id"]

    # Create a role or use an existing one
    roles_response = client.get("/roles/")
    role_1 = roles_response.json()[0]
    role_2 = roles_response.json()[1]

    # Add user to group with role
    response = client.post(
        f"/resource_server/groups/{new_group_data['id']}/users",
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
        f"/resource_server/groups/{new_group_data['id']}/users",
        json={"email": user_data["email"], "role_id": role_1["id"]},
    )
    assert response_add_user_again.status_code == 403

    # Verify user is in the group
    group_details = client.get(f"/groups/{new_group_data['id']}")
    group_users = group_details.json()["users"]
    find_user = next(user for user in group_users if user["id"] == user_id)
    assert find_user is not None
    assert find_user["role_name"] == role_1["role_name"]

    # Update user role in group
    updated_user_response = client.patch(
        f"/resource_server/groups/{new_group_data['id']}/users/{user_id}?role_id={role_2['id']}"
    )

    updated_user = updated_user_response.json()
    assert updated_user["email"] == user_data["email"]
    assert updated_user["role_name"] == role_2["role_name"]
    assert updated_user["is_admin"] is False

    # Verify user has new role in the group
    group_details = client.get(f"/groups/{new_group_data['id']}")
    group_users = group_details.json()["users"]
    find_user = next(user for user in group_users if user["id"] == user_id)
    assert find_user is not None
    assert find_user["role_name"] == role_2["role_name"]


def test_remove_user_from_group(client):
    """Test removing a user from a group."""
    new_group_data = create_group(client)

    user_data = random_user()
    create_user_response = client.post("/users/", json=user_data)
    user_id = create_user_response.json()["id"]

    roles_response = client.get("/roles/")
    role_id = roles_response.json()[0]["id"]

    # change user role
    client.patch(
        f"/resource_server/groups/{new_group_data['id']}/users/{user_id}?role_id={role_id}"
    )

    # Now remove the user from the group
    response = client.delete(
        f"/resource_server/groups/{new_group_data['id']}/users/{user_id}"
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

    admin = get_user(client, admin_email)
    admin_id = admin["id"]

    # Attempt to remove the only admin from the group
    response_delete_only_admin = client.delete(
        f"/resource_server/groups/{new_group_data['id']}/users/{admin_id}"
    )
    assert response_delete_only_admin.status_code == 403

    response_change_only_admin_role = client.patch(
        f"/resource_server/groups/{new_group_data['id']}/users/{admin_id}?role_id={2}"
    )
    assert response_change_only_admin_role.status_code == 403


def test_confirmation_email_sent_for_unverified_user(client):
    """Test that a confirmation email is sent when an unverified user is added to a group."""
    # Clear any previous emails in MailHog
    clear_mailhog_messages()

    # Create a new group (this creates an admin user)
    group_data = create_group(client)

    # Verify the admin user so they can act
    admin_sub = random_sub_pro_connect()

    # Create a new unverified user
    unverified_user = random_user()
    user_response = client.post("/users/", json=unverified_user)
    assert user_response.status_code == 201

    # Add the unverified user to the group (this should trigger confirmation email)
    add_user_data = {
        "email": unverified_user["email"],  # Use 'email' not 'user_email'
        "role_id": 2,  # Regular user role
    }

    response = client.post(
        f"/resource_server/groups/{group_data['id']}/users?acting_user_sub={admin_sub}",
        json=add_user_data,
    )
    if response.status_code != 201:
        print(f"Error response: {response.status_code} - {response.text}")
    assert response.status_code == 201

    # Assert that a confirmation email was sent to the unverified user
    assert_email_sent(
        unverified_user["email"], subject_contains="Activation de votre compte"
    )
