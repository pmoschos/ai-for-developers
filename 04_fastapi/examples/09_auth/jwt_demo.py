"""
09 — Authentication: JWT Create & Decode Demo

Run as a script:  python -m examples.09_auth.jwt_demo

A JWT is header.payload.signature — stateless, self-contained, signed.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(username: str) -> str:
    """Create a JWT with a subject (username) and expiry."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT. Returns the payload or None if invalid."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        print(f"JWT Error: {e}")
        return None


if __name__ == "__main__":
    token = create_access_token("alice")
    print(f"Token:   {token}")
    print(f"Decoded: {decode_access_token(token)}")
    print(f"Bad key: {decode_access_token('invalid.token.here')}")
