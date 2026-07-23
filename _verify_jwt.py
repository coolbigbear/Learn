"""Verify JWT token creation and verification works correctly."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from app.services.jwt import create_access_token, decode_access_token

# Create a token
token = create_access_token(user_id=42)
print(f"Token: {token[:50]}...")

# Decode it
payload = decode_access_token(token)
assert payload is not None, "Token should decode successfully"
assert payload["sub"] == "42", f"Expected sub=42, got sub={payload['sub']}"
print(f"Decoded payload: sub={payload['sub']}")

# Verify expiration is set
assert "exp" in payload, "Token should have expiration"
print(f"Token has expiration: {payload['exp']}")

# Invalid token should return None
bad_payload = decode_access_token("invalid-token")
assert bad_payload is None, "Invalid token should return None"
print("Invalid token correctly rejected")

# Expired token should return None
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM

expired_payload = {
    "sub": "42",
    "exp": datetime.now(timezone.utc) - timedelta(hours=1),
}
expired_token = jwt.encode(expired_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
result = decode_access_token(expired_token)
assert result is None, "Expired token should return None"
print("Expired token correctly rejected")

print("\nAll JWT verification tests passed!")