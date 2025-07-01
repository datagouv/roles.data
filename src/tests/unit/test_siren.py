# Test cases
import pytest
from fastapi import HTTPException

from src.model import validate_siret


@pytest.fixture
def valid_test_sirets():
    """Fixture providing valid SIRETs for testing."""
    return ["44011762001530", "13002526500013", "35600000000048"]


@pytest.fixture
def invalid_test_sirets():
    """Fixture providing invalid SIRETs for testing."""
    return [
        ("123456789000000", "fails Luhn checksum"),
        ("000000000000000", "fails Luhn checksum"),
        ("12345678000", "14-digit string"),
        ("12345678900000000", "14-digit string"),
        ("aaaaaaaaa00000", "14-digit string"),
        ("1234567", "14-digit string"),
    ]


def test_valid_sirets_with_fixture(valid_test_sirets):
    """Test valid SIRETs using fixture."""
    for siret in valid_test_sirets:
        result = validate_siret(siret)
        assert result == siret


def test_invalid_sirets_with_fixture(invalid_test_sirets):
    """Test invalid SIRETs using fixture."""
    for siret, expected_error_fragment in invalid_test_sirets:
        with pytest.raises(HTTPException) as exc_info:
            validate_siret(siret)

        assert exc_info.value.status_code == 400
        assert expected_error_fragment in exc_info.value.detail
