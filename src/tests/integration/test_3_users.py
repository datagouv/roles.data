from src.tests.helpers import random_user


def test_create_user(client):
    """Test creating a new user."""
    user_data = random_user()

    response = client.post("/users/", json={"email": user_data["email"]})

    # Check response
    assert response.status_code == 201  # Should be 201 Created
    user = response.json()
    assert user["email"] == user_data["email"]
    assert "id" in user


def test_get_user_by_id(client):
    """Test retrieving a user by ID."""
    # First create a user to get
    user_data = random_user()
    create_response = client.post("/users/", json={"email": user_data["email"]})
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
