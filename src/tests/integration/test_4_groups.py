from src.tests.helpers import create_group, random_sub_pro_connect


def test_list_groups(client):
    """Test listing all groups."""
    response = client.get("/groups/")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert any(group for group in groups if group["name"] == "stack technique")


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

    assert any(
        user for user in group["users"] if user["email"] == new_group["admin"]["email"]
    )
    assert any(
        user
        for user in group["users"]
        if user["email"] == new_group["members"][0]["email"]
    )

    new_group_bad_siren = create_group(client)
    new_group_bad_siren["organisation_siren"] = "aaaaaaaaa"
    response = client.post("/groups/", json=new_group_bad_siren)
    # invalid siren should return 400
    assert response.status_code == 400

    new_group_no_siren = create_group(client)
    del new_group_no_siren["organisation_siren"]

    response = client.post("/groups/", json=new_group_no_siren)
    # invalid siren should return 400
    assert response.status_code == 422

    new_group_empty_siren = create_group(client)
    new_group_empty_siren["organisation_siren"] = ""

    response = client.post("/groups/", json=new_group_empty_siren)
    # invalid siren should return 400
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


def test_search_group_by_user(client):
    """Test searching groups by user email"""
    # Create a new group
    new_group_data = create_group(client)

    random_sub = random_sub_pro_connect()

    responseNotVerified = client.get(
        "/groups/search", params={"email": new_group_data["admin"]["email"]}
    )
    assert responseNotVerified.status_code == 423

    response = client.get(
        "/groups/search",
        params={
            "email": new_group_data["admin"]["email"],
            "acting_user_sub": random_sub,
        },
    )

    assert response.status_code == 200
    group = response.json()
    assert isinstance(group, list)
    assert len(group) == 1
    assert group[0]["name"] == new_group_data["name"]
    assert group[0]["organisation_siren"] == new_group_data["organisation_siren"]
    assert group[0]["scopes"] == new_group_data["scopes"]
    assert group[0]["contract"] == new_group_data["contract"]

    assert any(
        (
            user
            for user in group[0]["users"]
            if user["email"] == new_group_data["admin"]["email"]
        )
    )

    # Test non-existent user
    response404 = client.get(
        "/groups/search",
        params={"email": "hey@test.fr", "acting_user_sub": random_sub_pro_connect()},
    )
    assert response404.status_code == 404

    # Test non-existent group
    responseEmpty = client.get(
        "/groups/search",
        params={
            "email": "user-not-in-group@beta.gouv.fr",
            "acting_user_sub": random_sub_pro_connect(),
        },
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
