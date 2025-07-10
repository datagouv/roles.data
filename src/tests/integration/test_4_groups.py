from src.tests.helpers import (
    create_group,
    random_group,
    random_sub_pro_connect,
    random_user,
    verify_user,
)


def test_list_groups(client):
    """Test listing all groups."""
    response = client.get("/groups/")
    assert response.status_code == 200
    groups = response.json()
    assert isinstance(groups, list)
    assert any(group for group in groups if group["name"] == "stack technique")


def test_create_group_no_acting_user(client):
    """Test creating a new group without an acting user."""

    new_group_data = random_group()

    # missing acting_user_sub or no_acting_user, should return 400
    response = client.post("/groups", json=new_group_data)
    assert response.status_code == 400

    # invalid UUID acting_user_sub, should return 400
    response = client.post("/groups/?acting_user_sub=abc", json=new_group_data)
    assert response.status_code == 400

    # valid UUID acting_user_sub, should return 200
    response = client.post(
        "/groups/?acting_user_sub=2c5aa869-80be-48be-b7cc-0f3f5521e1f7",
        json=new_group_data,
    )
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
    assert group["contract"] == new_group["contract"]

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


def test_search_group_by_user(client):
    """Test searching groups by user email"""
    # Create a new group
    new_group_data = create_group(client)

    random_sub = random_sub_pro_connect()

    responseNotVerified = client.get(
        "/groups/search", params={"user_email": new_group_data["admin"]["email"]}
    )
    assert responseNotVerified.status_code == 422

    response = client.get(
        "/groups/search",
        params={
            "user_email": new_group_data["admin"]["email"],
            "user_sub": random_sub,
        },
    )

    assert response.status_code == 200
    group = response.json()
    assert isinstance(group, list)
    assert len(group) == 1
    assert group[0]["name"] == new_group_data["name"]
    assert group[0]["organisation_siret"] == new_group_data["organisation_siret"]
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
        params={"user_email": "hey@test.fr", "user_sub": random_sub_pro_connect()},
    )
    assert response404.status_code == 404

    userResponse = client.post("/users", json=random_user())
    assert userResponse.status_code == 201
    user = userResponse.json()

    # Test non-existent group
    responseEmpty = client.get(
        "/groups/search",
        params={
            "user_email": user["email"],
            "user_sub": random_sub_pro_connect(),
        },
    )
    assert responseEmpty.status_code == 200
    group = responseEmpty.json()
    assert isinstance(group, list)
    assert len(group) == 0


def test_get_group_verify_conflict(client):
    new_group_data = create_group(client)

    admin = new_group_data["admin"]["email"]
    verify_user(client, admin, random_sub_pro_connect())

    random_sub = random_sub_pro_connect()
    response = client.get(
        "/groups/search",
        params={
            "user_email": new_group_data["admin"]["email"],
            "user_sub": random_sub,
        },
    )
    # Verify user with a different sub should return 406
    assert response.status_code == 406


def test_get_group_not_found(client):
    """Test retrieving a non-existent group."""
    # Test non-existent group
    response = client.get("/groups/999999")
    assert response.status_code == 404
