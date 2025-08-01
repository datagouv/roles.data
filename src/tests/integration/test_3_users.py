from src.tests.helpers import random_sub_pro_connect, random_user


def test_create_user(client):
    """Test creating a new user."""
    user_data = random_user()

    response = client.post("/users/", json=user_data)

    # Check response
    assert response.status_code == 201  # Should be 201 Created
    user = response.json()
    assert user["email"] == user_data["email"]
    assert "id" in user


def test_get_user_by_id(client):
    """Test retrieving a user by ID."""
    # First create a user to get
    user_data = random_user()
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    # This should succeed but has a bug (no return statement in the route)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id
    assert user["email"] == user_data["email"]


def test_get_nonexistent_user(client):
    """Test retrieving a non-existent user."""
    # Use a large ID that shouldn't exist
    response = client.get("/users/999999")

    # Should return 404 Not Found
    assert response.status_code == 404


def test_get_user_by_email(client):
    """Test retrieving a user by email."""
    user_data = random_user()
    client.post("/users/", json=user_data)

    # Get user by email
    response = client.get("/users/search", params={"email": user_data["email"]})

    # Check response
    assert response.status_code == 200
    user = response.json()
    assert user["email"] == user_data["email"]

    # Verify not found case
    response = client.get("/users/search", params={"email": "notfound@example.com"})
    assert response.status_code == 404


def test_uuid_format(client):
    """Test that the user ID is in UUID format."""
    user_data = random_user()
    response = client.post("/users/", json=user_data)
    user = response.json()

    response_verify = client.patch(
        "/users/verify",
        params={"user_email": user["email"], "user_sub": "blbabla_test"},
    )

    # not a valid uuid v4
    assert response_verify.status_code == 422

    response_verify_ok = client.patch(
        "/users/verify",
        params={"user_email": user["email"], "user_sub": random_sub_pro_connect()},
    )

    assert response_verify_ok.status_code == 200
    assert response_verify_ok.json()["is_verified"] is not False
