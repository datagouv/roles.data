from src.tests.helpers import random_group


def test_grant_access(client):
    """Test granting access to a group."""
    # Create a group
    group_data = random_group()
    group_response = client.post("/groups/", json=group_data)
    group_id = group_response.json()["id"]

    # Grant access with scopes
    scopes = "read,write"
    response = client.post(f"/groups/{group_id}/grant-access?scopes={scopes}")
    assert response.status_code == 200

    # Verify access was granted - implementation dependent


def test_update_access(client):
    """Test updating access for a group."""
    # Create a group
    group_data = random_group()
    group_response = client.post("/groups/", json=group_data)
    group_id = group_response.json()["id"]

    # First grant access
    client.post(f"/groups/{group_id}/grant-access?scopes=read")

    # Update access with new scopes
    new_scopes = "read,write,delete"
    response = client.put(f"/groups/{group_id}/update-access?scopes={new_scopes}")
    assert response.status_code == 200

    # Verify access was updated - implementation dependent
