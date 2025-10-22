import random
import string
from contextlib import contextmanager
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import httpx

DINUM_SIRET = "13002526500013"


def random_group():
    """Generate random group data."""
    return {
        "name": f"Test Group {''.join(random.choices(string.ascii_lowercase, k=5))}",
        "organisation_siret": DINUM_SIRET,
        "admin": {"email": f"admin_{random.randint(1000, 9999)}@beta.gouv.fr"},
        "scopes": "read maintain",
        "contract_description": "datapass_test",
        "contract_url": "https://example.com/contract",
        "members": [{"email": f"member_{random.randint(1000, 9999)}@beta.gouv.fr"}],
    }


def random_sub_pro_connect():
    """Generate a random sub ProConnect."""
    return uuid4()


def random_user():
    """Generate a random user for testing."""
    return {
        "email": f"test_{uuid4()}@beta.gouv.fr",
        "sub_pro_connect": uuid4(),
    }


def random_name():
    """Generate a random name."""
    return f"Test Name {''.join(random.choices(string.ascii_lowercase, k=5))}"


def create_group(client, admin_email=None):
    """Create a group for testing."""
    new_group_data = random_group()

    if admin_email:
        new_group_data["admin"]["email"] = admin_email

    response = client.post("/groups/?no_acting_user=True", json=new_group_data)
    assert response.status_code == 201
    group = response.json()
    assert group["name"] == new_group_data["name"]
    new_group_data["id"] = group["id"]
    return new_group_data


def get_user(client, user_email):
    response = client.get("/users/search", params={"email": user_email})
    assert response.status_code == 200
    user = response.json()
    return user


def get_group(client, group_id):
    response = client.get(f"/groups/{group_id}")
    assert response.status_code == 200
    group = response.json()
    return group


def resource_server_auth_headers(sub: str | UUID, email: str) -> dict:
    """
    Create fake Authorization header for resource server tests.
    """
    sub_str = str(sub)
    token = f"test:{sub_str}:{email}"
    return {"Authorization": f"Bearer {token}"}


# MailHog testing helpers
def get_mailhog_messages(mailhog_url="http://localhost:8025"):
    """Get all messages from MailHog."""
    response = httpx.get(f"{mailhog_url}/api/v2/messages")
    response.raise_for_status()
    return response.json().get("items", [])


def clear_mailhog_messages(mailhog_url="http://localhost:8025"):
    """Clear all messages from MailHog."""
    response = httpx.delete(f"{mailhog_url}/api/v1/messages")
    response.raise_for_status()


def assert_email_sent(
    recipient_email, subject_contains="", mailhog_url="http://localhost:8025"
):
    """Assert that an email was sent to a recipient with optional subject check."""
    messages = get_mailhog_messages(mailhog_url)
    email = None
    for msg in messages:
        for recipient in msg.get("To", []):
            if (
                recipient.get("Mailbox") == recipient_email.split("@")[0]
                and recipient.get("Domain") == recipient_email.split("@")[1]
            ):
                email = msg
                break

    assert email is not None, f"No email found for {recipient_email}"

    if subject_contains:
        subject = email.get("Content", {}).get("Headers", {}).get("Subject", [""])[0]
        assert (
            subject_contains in subject
        ), f"Subject '{subject}' doesn't contain '{subject_contains}'"

    return email


@contextmanager
def mock_session(session_data: dict):
    """
    Context manager to mock session data in FastAPI requests.

    Usage:
        with mock_session({"user_email": "test@example.com"}):
            response = client.get("/some-endpoint")
    """

    def mock_session_get(key, default=None):
        return session_data.get(key, default)

    mock_session_obj = Mock()
    mock_session_obj.get = mock_session_get

    with patch("starlette.requests.Request.session", mock_session_obj):
        yield
