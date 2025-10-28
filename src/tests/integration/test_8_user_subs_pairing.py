"""
Integration tests for user-sub pairing functionality.

These tests verify the email-sub pairing logic that prevents a user's ProConnect sub
from being changed after initial pairing. Tests use resource server endpoints to trigger
the pairing logic.
"""

from src.tests.helpers import (
    create_group,
    random_user,
    resource_server_auth_headers,
)


def test_first_pairing_allows_group_access(client):
    """Test that first pairing saves the sub and allows access."""
    user = random_user()

    # Create group with user as admin (user has no sub yet)
    group = create_group(client, admin_email=user["email"])

    # First access with resource server - should pair and succeed
    headers = resource_server_auth_headers(user["sub_pro_connect"], user["email"])
    response = client.get("/resource-server/groups/", headers=headers)

    assert response.status_code == 200
    groups = response.json()
    # User should see their group
    assert any(g["id"] == group["id"] for g in groups)


def test_same_sub_allows_repeated_access(client):
    """Test that using the same sub multiple times works correctly."""
    user = random_user()

    # Create group
    group = create_group(client, admin_email=user["email"])
    headers = resource_server_auth_headers(user["sub_pro_connect"], user["email"])

    # First access - pairs the sub
    response1 = client.get("/resource-server/groups/", headers=headers)
    assert response1.status_code == 200

    # Second access - same sub should work
    response2 = client.get("/resource-server/groups/", headers=headers)
    assert response2.status_code == 200
    groups = response2.json()
    assert any(g["id"] == group["id"] for g in groups)

    # Third access - still works
    response3 = client.get("/resource-server/groups/", headers=headers)
    assert response3.status_code == 200


def test_different_sub_fails_after_pairing(client):
    """Test that pairing fails with 403 when sub doesn't match existing sub."""
    user = random_user()
    different_sub = random_user()["sub_pro_connect"]

    # Create group
    create_group(client, admin_email=user["email"])

    # First access - pairs original sub
    headers1 = resource_server_auth_headers(user["sub_pro_connect"], user["email"])
    response1 = client.get("/resource-server/groups/", headers=headers1)
    assert response1.status_code == 200

    # Try to access with different sub for same email - should fail
    headers2 = resource_server_auth_headers(different_sub, user["email"])
    response2 = client.get("/resource-server/groups/", headers=headers2)

    # Should fail with 403 Forbidden due to sub mismatch
    assert response2.status_code == 403
    assert "different sub" in response2.json()["detail"].lower()


def test_nonexistent_user_fails_pairing(client):
    """Test that pairing fails with 403 for users that don't exist in database."""
    user = random_user()

    # Try to access resource server without creating user first
    headers = resource_server_auth_headers(user["sub_pro_connect"], user["email"])
    response = client.get("/resource-server/groups/", headers=headers)

    # Should fail with 403 because user doesn't exist
    assert response.status_code == 403
    assert "not found" in response.json()["detail"].lower()
