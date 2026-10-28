from unittest.mock import patch
from uuid import uuid4

import pytest

from src.repositories.users_in_group import UsersInGroupRepository
from src.services.email.main import EmailService
from src.tests.helpers import (
    create_group,
    random_group,
    random_user,
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


def test_create_group_failure_rolls_back_everything(client, user_exists):
    """Test that a failure while creating a group leaves neither the group nor its admin."""
    new_group_data = random_group()
    new_group_data["admin"]["email"] = random_user()["email"]

    with (
        patch.object(
            UsersInGroupRepository, "add_users", side_effect=RuntimeError("DB error")
        ),
        pytest.raises(RuntimeError),
    ):
        client.post("/groups/?no_acting_user=True", json=new_group_data)

    assert not user_exists(new_group_data["admin"]["email"])
    groups = client.get("/groups/all").json()
    assert all(group["name"] != new_group_data["name"] for group in groups)


def test_create_group_sends_admin_email_once_committed(client):
    """Test that the admin is notified once the group is created."""
    new_group_data = random_group()

    with patch.object(EmailService, "nouveau_groupe_email") as mock_email:
        response = client.post("/groups/?no_acting_user=True", json=new_group_data)

    assert response.status_code == 201
    mock_email.assert_called_once()
    assert mock_email.call_args.kwargs["recipients"] == [
        new_group_data["admin"]["email"]
    ]
    assert mock_email.call_args.kwargs["group_admin_email"] is None


def test_create_group_failure_does_not_send_admin_email(client):
    """Test that the admin is not notified when the group creation is rolled back."""
    new_group_data = random_group()

    with (
        # Adding the admin succeeds, adding the members fails
        patch.object(
            UsersInGroupRepository,
            "add_users",
            side_effect=[None, RuntimeError("DB error")],
        ),
        patch.object(EmailService, "nouveau_groupe_email") as mock_email,
        pytest.raises(RuntimeError),
    ):
        client.post("/groups/?no_acting_user=True", json=new_group_data)

    mock_email.assert_not_called()


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


@pytest.mark.parametrize("personal_email_domain", ["gmail.com", "Gmail.COM"])
def test_create_group_personal_admin_email_is_refused(
    client, user_exists, personal_email_domain
):
    """Test that an admin at a personal mail provider creates neither group nor user."""
    new_group_data = random_group()
    personal_email = f"admin_{uuid4()}@{personal_email_domain}"
    new_group_data["admin"]["email"] = personal_email
    # A random_group member email may already exist from an earlier test
    new_group_data["members"] = [{"email": f"member_{uuid4()}@beta.gouv.fr"}]

    response = client.post("/groups/?no_acting_user=True", json=new_group_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "PERSONAL_EMAIL_REFUSED"}
    assert not user_exists(personal_email.lower())
    assert not user_exists(new_group_data["members"][0]["email"])
    groups = client.get("/groups/all").json()
    assert all(group["name"] != new_group_data["name"] for group in groups)


def test_create_group_personal_member_email_is_refused(client, user_exists):
    """Test that a member at a personal mail provider creates neither group nor user."""
    new_group_data = random_group()
    # A random_group admin email may already exist from an earlier test
    new_group_data["admin"]["email"] = f"admin_{uuid4()}@beta.gouv.fr"
    first_personal_email = f"member_{uuid4()}@free.fr"
    second_personal_email = f"member_{uuid4()}@Bbox.FR"
    new_group_data["members"] = [
        {"email": second_personal_email},
        {"email": first_personal_email},
    ]

    response = client.post("/groups/?no_acting_user=True", json=new_group_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "PERSONAL_EMAIL_REFUSED"}
    assert not user_exists(new_group_data["admin"]["email"])
    assert not user_exists(first_personal_email.lower())
    assert not user_exists(second_personal_email.lower())
    groups = client.get("/groups/all").json()
    assert all(group["name"] != new_group_data["name"] for group in groups)


def test_create_group_accepts_a_sub_domain_of_a_personal_provider(client):
    """Test that only the exact domains are refused, not their sub-domains."""
    new_group_data = random_group()
    new_group_data["admin"]["email"] = f"admin_{uuid4()}@mail.gmail.com"

    response = client.post("/groups/?no_acting_user=True", json=new_group_data)

    assert response.status_code == 201
    group = client.get(f"/groups/{response.json()['id']}").json()
    assert any(
        user["email"] == new_group_data["admin"]["email"] for user in group["users"]
    )
