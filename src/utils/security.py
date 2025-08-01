import secrets
import string

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=8,  # Optimized for performance: ~25ms vs ~200ms with default 12 rounds
)


def verify_password(plain_password, hashed_password):
    """Verify passwords match"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def generate_random_password(length=32):
    """Generate a random password with letters, digits, and special characters."""
    alphabet = string.ascii_letters + string.digits + "~+=-_."
    return "".join(secrets.choice(alphabet) for _ in range(length))
