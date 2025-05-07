import random
import string

DINUM_SIREN = "130025265"


def random_group():
    """Generate random group data."""
    return {
        "name": f"Test Group {''.join(random.choices(string.ascii_lowercase, k=5))}",
        "organisation_siren": DINUM_SIREN,
        "admin_email": f"admin_{random.randint(1000, 9999)}@example.com",
    }


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
        is None
    )


def test_get_group_not_found(client):
    """Test retrieving a non-existent group."""
    # Test non-existent group
    response = client.get("/groups/999999")
    assert response.status_code == 404


# def test_update_group(client):
#     """Test updating a group's name."""
#     # First create a group
#     group_data = random_group()
#     create_response = client.post("/groups/", json=group_data)
#     assert create_response.status_code == 200
#     group_id = create_response.json()["id"]

#     # Update the group name
#     new_name = f"Updated Group {''.join(random.choices(string.ascii_lowercase, k=5))}"
#     response = client.put(f"/groups/{group_id}?group_name={new_name}")
#     assert response.status_code == 200

#     updated_group = response.json()
#     assert updated_group["id"] == group_id
#     assert updated_group["name"] == new_name

#     # Test non-existent group
#     response = client.put(f"/groups/999999?group_name={new_name}")
#     assert response.status_code == 404

# def test_add_user_to_group(client):
#     """Test adding a user to a group."""
#     # Create a group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     # Create a user
#     user_data = {
#         "email": f"test_{random.randint(1000, 9999)}@example.com",
#         "sub_pro_connect": f"sub_{random.randint(1000, 9999)}"
#     }
#     user_response = client.post("/users/", json=user_data)
#     user_id = user_response.json()["id"]

#     # Create a role or use an existing one
#     roles_response = client.get("/roles/")
#     role_id = roles_response.json()[0]["id"]

#     # Add user to group with role
#     response = client.post(f"/groups/{group_id}/users/{user_id}?role_id={role_id}")
#     assert response.status_code == 201

#     # Verify user is in the group
#     group_details = client.get(f"/groups/{group_id}")
#     group_users = group_details.json()["users"]
#     assert any(user["id"] == user_id for user in group_users)

# def test_remove_user_from_group(client):
#     """Test removing a user from a group."""
#     # Setup: create group, user, and add user to group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     user_data = {
#         "email": f"test_{random.randint(1000, 9999)}@example.com",
#         "sub_pro_connect": f"sub_{random.randint(1000, 9999)}"
#     }
#     user_response = client.post("/users/", json=user_data)
#     user_id = user_response.json()["id"]

#     roles_response = client.get("/roles/")
#     role_id = roles_response.json()[0]["id"]

#     # Add user to group
#     client.post(f"/groups/{group_id}/users/{user_id}?role_id={role_id}")

#     # Now remove the user from the group
#     response = client.delete(f"/groups/{group_id}/users/{user_id}")
#     assert response.status_code == 204

#     # Verify user is not in the group
#     group_details = client.get(f"/groups/{group_id}")
#     group_users = group_details.json()["users"]
#     assert not any(user["id"] == user_id for user in group_users)

# def test_update_user_role_in_group(client):
#     """Test updating a user's role in a group."""
#     # Setup: create group, user, and add user to group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     user_data = {
#         "email": f"test_{random.randint(1000, 9999)}@example.com",
#         "sub_pro_connect": f"sub_{random.randint(1000, 9999)}"
#     }
#     user_response = client.post("/users/", json=user_data)
#     user_id = user_response.json()["id"]

#     # Get roles
#     roles_response = client.get("/roles/")
#     roles = roles_response.json()
#     original_role_id = roles[0]["id"]
#     new_role_id = roles[1]["id"] if len(roles) > 1 else roles[0]["id"]

#     # Add user to group with initial role
#     client.post(f"/groups/{group_id}/users/{user_id}?role_id={original_role_id}")

#     # Update user's role
#     response = client.put(f"/groups/{group_id}/users/{user_id}?role_id={new_role_id}")
#     assert response.status_code == 200

#     # Verify role was updated - would need a way to check user's role in group

# def test_grant_access(client):
#     """Test granting access to a group."""
#     # Create a group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     # Grant access with scopes
#     scopes = "read,write"
#     response = client.post(f"/groups/{group_id}/grant-access?scopes={scopes}")
#     assert response.status_code == 200

#     # Verify access was granted - implementation dependent

# def test_update_access(client):
#     """Test updating access for a group."""
#     # Create a group
#     group_data = random_group()
#     group_response = client.post("/groups/", json=group_data)
#     group_id = group_response.json()["id"]

#     # First grant access
#     client.post(f"/groups/{group_id}/grant-access?scopes=read")

#     # Update access with new scopes
#     new_scopes = "read,write,delete"
#     response = client.put(f"/groups/{group_id}/update-access?scopes={new_scopes}")
#     assert response.status_code == 200

#     # Verify access was updated - implementation dependent
