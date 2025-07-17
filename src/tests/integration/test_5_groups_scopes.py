from src.tests.helpers import create_group


def test_update_scopes(client):
    """Test granting access to a group."""
    # Update access with new scopes
    new_group_data = create_group(client)

    new_scopes = "read,write,delete"
    new_contract = "datapass_48"
    response = client.patch(
        f"/groups/{new_group_data["id"]}/scopes?scopes={new_scopes}&contract_description={new_contract}"
    )
    assert response.status_code == 200

    # Verify access was updated
    response = client.get(f"/groups/{new_group_data["id"]}")
    assert response.status_code == 200
    group = response.json()
    assert group["scopes"] == new_scopes
    assert group["contract_description"] == new_contract
