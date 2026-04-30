"""
Security — Password Hashing & JWT Token Helpers

Provides:
  - hash_password(raw) → hashed string
  - verify_password(raw, hashed) → bool
  - create_access_token(subject) → JWT string
"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# --- Password Hashing ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(raw, hashed)


# --- JWT Tokens ---


def create_access_token(sub: str) -> str:
    """Create a signed JWT with a subject and expiry."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
