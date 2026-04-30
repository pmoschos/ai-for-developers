"""
09 — Authentication: Password Hashing with bcrypt

Run as a script:  python -m examples.09_auth.password_hashing

Never store passwords in plain text!
bcrypt is the safe default — it's slow on purpose to resist brute-force attacks.
"""

from passlib.context import CryptContext

# Create a password context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    """Hash a plain-text password. Returns a bcrypt hash string."""
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(raw, hashed)


if __name__ == "__main__":
    password = "correct-horse-battery-staple"
    hashed = hash_password(password)

    print(f"Password:  {password}")
    print(f"Hash:      {hashed}")
    print(f"Verify OK: {verify_password(password, hashed)}")
    print(f"Verify bad:{verify_password('wrong-password', hashed)}")
