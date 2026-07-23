"""JWT token creation and verification.

Uses python-jose with HS256 symmetric signing.
Access tokens include a configurable expiration (default 60 minutes).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY


def create_access_token(user_id: int, username: str = "") -> str:
    """Create a signed JWT access token for the given user.

    The token encodes the user ID as the 'sub' (subject) claim, the
    username as the 'username' claim, and includes an 'exp' (expiration)
    claim set to now + configured minutes.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "username": username,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and verify a JWT access token.

    Returns the decoded payload dict on success, or None if the token
    is malformed, expired, or has an invalid signature.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None