from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import get_settings
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
            "type": "access",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        get_settings().jwt_secret_key.get_secret_value(),
        algorithms=["HS256"],
        options={"require": ["sub", "iat", "exp", "type"]},
    )
    subject = payload["sub"]
    if (
        payload["type"] != "access"
        or not isinstance(subject, str)
        or not subject.isdecimal()
    ):
        raise jwt.InvalidTokenError("Token invalid token")
    try:
        user_id = int(subject)
    except ValueError as error:
        raise jwt.InvalidTokenError("Token invalido") from error
    if user_id < 1:
        raise jwt.InvalidTokenError("Token invalido")
    return user_id
