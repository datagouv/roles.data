async def test_create_user(client):
    """Test that we can list all roles."""
    response = await client.get("/roles/")
    assert response.status_code == 200

    roles = response.json()
    assert len(roles) >= 2

    # Verify admin role exists
    admin_role = next((r for r in roles if r["role_name"] == "admin"), None)
    assert admin_role is not None
    assert admin_role["is_admin"] is True
