import random
import string
from uuid import uuid4

DINUM_SIREN = "130025265"


def random_group():
    """Generate random group data."""
    return {
        "name": f"Test Group {''.join(random.choices(string.ascii_lowercase, k=5))}",
        "organisation_siren": DINUM_SIREN,
        "admin_email": f"admin_{random.randint(1000, 9999)}@example.com",
        "scopes": "read maintain",
        "contract": "datapass_test",
    }


def random_user():
    """Generate a random user for testing."""
    return {"email": f"test_{uuid4()}@example.com", "sub_pro_connect": f"sub_{uuid4()}"}


def random_name():
    """Generate a random name."""
    return f"Test Name {''.join(random.choices(string.ascii_lowercase, k=5))}"
