"""Хеширование паролей и JWT (роли: пользователь / администратор)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import settings

Role = Literal["user", "admin"]
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def _create_token(subject: str, token_type: str, expires: timedelta, role: str | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires,
        "jti": uuid.uuid4().hex,
    }
    if role:
        payload["role"] = role
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: int, role: str) -> str:
    return _create_token(
        str(user_id),
        TOKEN_TYPE_ACCESS,
        timedelta(minutes=settings.access_token_ttl_minutes),
        role=role,
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        str(user_id),
        TOKEN_TYPE_REFRESH,
        timedelta(days=settings.refresh_token_ttl_days),
    )


def decode_token(token: str, expected_type: str = TOKEN_TYPE_ACCESS) -> dict[str, Any] | None:
    """Возвращает payload или None, если токен невалиден/просрочен/чужого типа."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload
