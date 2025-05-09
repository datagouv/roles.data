def test_get_all_roles(client):
    """Test retrieving all roles."""
    response = client.get("/roles/")

    # Verify response
    assert response.status_code == 200

    # Check that we get a list
    roles = response.json()
    assert isinstance(roles, list)

    # There should be at least 2 default roles
    assert len(roles) >= 2

    # Verify at least one admin role exists
    admin_role = next((r for r in roles if r["role_name"] == "administrateur"), None)
    assert admin_role is not None
    assert admin_role["is_admin"] is True

    # Verify user role exists
    user_role = next((r for r in roles if r["role_name"] == "agent"), None)
    assert user_role is not None
    assert user_role["is_admin"] is False


def test_get_role_by_id(client):
    """Test retrieving a specific role by ID."""
    # Get all roles first to find a valid ID
    all_roles = client.get("/roles/").json()

    # Get the first role's ID
    first_role_id = all_roles[0]["id"]
    first_role_name = all_roles[0]["role_name"]

    # Retrieve the specific role
    response = client.get(f"/roles/{first_role_id}")

    # Verify response
    assert response.status_code == 200
    role = response.json()

    # Check role data
    assert role["id"] == first_role_id
    assert role["role_name"] == first_role_name
    assert "is_admin" in role


def test_get_role_by_id_not_found(client):
    """Test retrieving a non-existent role ID."""
    # Use a very large ID that shouldn't exist
    response = client.get("/roles/99999")

    # Should return 404 Not Found
    assert response.status_code == 404
