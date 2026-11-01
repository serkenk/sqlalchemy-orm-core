from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from config import settings

# OAuth2 scheme for Swagger UI token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Initialize password hasher with bcrypt
password_hash = PasswordHash((BcryptHasher(),))


# --- Password Hashing Utilities ---
def get_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against its corresponding hash."""
    return password_hash.verify(plain_password, hashed_password)


# --- JWT Token Utilities ---
def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Generates a signed JWT access token containing the subject claim (e.g., user_id)."""
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "exp": expire,
        "sub": str(subject),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodes and validates a JWT access token.

    Raises jwt.PyJWTError if the token is invalid or expired.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    return payload
