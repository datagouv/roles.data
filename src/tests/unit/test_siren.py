# Test cases
import pytest
from fastapi import HTTPException

from src.model import validate_siren


@pytest.fixture
def valid_test_sirens():
    """Fixture providing valid SIRENs for testing."""
    return ["732829320", "440117620", "130020649", "356000000"]


@pytest.fixture
def invalid_test_sirens():
    """Fixture providing invalid SIRENs for testing."""
    return [
        ("123456789", "fails Luhn checksum"),
        ("000000000", "fails Luhn checksum"),
        ("12345678", "9-digit string"),
        ("1234567890", "9-digit string"),
        ("aaaaaaaaa", "9-digit string"),
        ("1234567", "9-digit string"),
    ]


def test_valid_sirens_with_fixture(valid_test_sirens):
    """Test valid SIRENs using fixture."""
    for siren in valid_test_sirens:
        result = validate_siren(siren)
        assert result == siren


def test_invalid_sirens_with_fixture(invalid_test_sirens):
    """Test invalid SIRENs using fixture."""
    for siren, expected_error_fragment in invalid_test_sirens:
        with pytest.raises(HTTPException) as exc_info:
            validate_siren(siren)

        assert exc_info.value.status_code == 400
        assert expected_error_fragment in exc_info.value.detail
