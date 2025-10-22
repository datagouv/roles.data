from src.tests.helpers import (
    create_group,
    random_group,
)


def test_list_groups(client):
    """Test listing all groups."""
    response = client.get("/groups/all")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert any(group for group in groups if group["name"] == "stack technique")


def test_create_group_no_acting_user(client):
    """Test creating a new group without an acting user."""

    new_group_data = random_group()

    # missing acting_user_sub or no_acting_user, should return 400
    response = client.post("/groups", json=new_group_data)
    assert response.status_code == 201


def test_create_group(client):
    """Test creating a new group."""
    new_group = create_group(client)

    response = client.get(f"/groups/{new_group['id']}")

    assert response.status_code == 200
    group = response.json()
    assert "id" in group
    assert group["name"] == new_group["name"]
    assert group["organisation_siret"] == new_group["organisation_siret"]
    assert group["scopes"] == new_group["scopes"]
    assert group["contract_description"] == new_group["contract_description"]
    assert group["contract_url"] == new_group["contract_url"]

    assert any(
        user for user in group["users"] if user["email"] == new_group["admin"]["email"]
    )
    assert any(
        user
        for user in group["users"]
        if user["email"] == new_group["members"][0]["email"]
    )

    new_group_bad_siret = create_group(client)
    new_group_bad_siret["organisation_siret"] = "aaaaaaaaa"
    response = client.post("/groups/", json=new_group_bad_siret)
    # invalid siret should return 400
    assert response.status_code == 400

    new_group_no_siret = create_group(client)
    del new_group_no_siret["organisation_siret"]

    response = client.post("/groups/", json=new_group_no_siret)
    # no siret should return 422
    assert response.status_code == 422

    new_group_empty_siret = create_group(client)
    new_group_empty_siret["organisation_siret"] = ""

    response = client.post("/groups/", json=new_group_empty_siret)
    # invalid siret should return 400
    assert response.status_code == 400


def test_get_group_with_users(client):
    """Test retrieving a group with its users."""
    # Create a new group
    new_group_data = create_group(client)

    response = client.get(f"/groups/{new_group_data['id']}")
    assert response.status_code == 200
    group = response.json()
    assert group["name"] == new_group_data["name"]
    assert "users" in group  # Should include users array, even if empty
    assert any(
        user
        for user in group["users"]
        if user["email"] == new_group_data["admin"]["email"]
    )


def test_get_group_not_found(client):
    """Test retrieving a non-existent group."""
    # Test non-existent group
    response = client.get("/groups/999999")
    assert response.status_code == 404
