from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)

# We call the `bcrypt` library directly (rather than through passlib's
# CryptContext) to avoid a known passlib<->bcrypt>=4.1 version-detection
# incompatibility. bcrypt truncates at 72 bytes by design, so long
# passwords are truncated deterministically before hashing/verifying.
_MAX_BCRYPT_BYTES = 72


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw_bytes = plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    try:
        return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return subject
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")


async def get_current_user_optional(token: str | None = Depends(oauth2_scheme)) -> str | None:
    """Public endpoints stay usable without auth (portfolio/demo friendliness),
    but if a bearer token IS supplied, it must be valid."""
    if token is None:
        return None
    return decode_access_token(token)


async def get_current_user_required(token: str | None = Depends(oauth2_scheme)) -> str:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return decode_access_token(token)
