import random
import string
from uuid import uuid4

DINUM_SIRET = "13002526500013"


def random_group():
    """Generate random group data."""
    return {
        "name": f"Test Group {''.join(random.choices(string.ascii_lowercase, k=5))}",
        "organisation_siret": DINUM_SIRET,
        "admin": {"email": f"admin_{random.randint(1000, 9999)}@example.com"},
        "scopes": "read maintain",
        "contract": "datapass_test",
        "members": [{"email": f"member_{random.randint(1000, 9999)}@example.com"}],
    }


def random_sub_pro_connect():
    """Generate a random sub ProConnect."""
    return uuid4()


def random_user():
    """Generate a random user for testing."""
    return {"email": f"test_{uuid4()}@example.com", "sub_pro_connect": f"sub_{uuid4()}"}


def random_name():
    """Generate a random name."""
    return f"Test Name {''.join(random.choices(string.ascii_lowercase, k=5))}"


def create_group(client):
    """Create a group for testing."""
    new_group_data = random_group()
    response = client.post("/groups/?acting_user_sub=False", json=new_group_data)
    assert response.status_code == 201
    group = response.json()
    assert group["name"] == new_group_data["name"]
    new_group_data["id"] = group["id"]
    return new_group_data


def verify_user(client, user_email, user_sub):
    """Verify a user by email and sub."""
    response = client.patch(
        "/users/verify", params={"user_email": user_email, "user_sub": user_sub}
    )
    assert response.status_code == 200
