"""Зависимости FastAPI: текущий пользователь и проверка ролей.

Роли ТЗ 3.1.1: гость (без токена), пользователь, администратор. Гость видит
только открытые справочники и каталог; пользователь работает со своими
проектами; администратор управляет справочниками и каталогом.

Роль берётся из базы, а не из токена: иначе понижение прав до сих пор
осталось бы в силе до истечения токена.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.errors import AppError
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.models import User

bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated["User | None", Depends(lambda: None)]  # переопределяется ниже


def get_optional_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)] = None,
) -> User | None:
    """Пользователь, если токен предъявлен и корректен; иначе None (гость)."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials, TOKEN_TYPE_ACCESS)
    if payload is None:
        # Неразбираемый токен не должен ронять запрос: гость может смотреть
        # каталог. Ошибка будет возвращена там, где доступ действительно нужен.
        return None
    subject = payload.get("sub")
    if not subject or not str(subject).isdigit():
        return None
    user = db.scalar(select(User).where(User.id == int(subject)))
    if user is None or not user.is_active:
        return None
    return user


def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise AppError(
            "Требуется вход в систему.",
            code="unauthorized",
            hint="Передайте заголовок Authorization: Bearer <токен>.",
            status_code=401,
        )
    return user


def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user.is_admin:
        raise AppError(
            "Операция доступна только администратору.",
            code="forbidden",
            hint=f"У вашей учётной записи роль «{user.role}».",
            status_code=403,
        )
    return user


#: Гость: пользователь не нужен вовсе. Требование, чтобы забытый токен не
#: превращал чтение каталога в ошибку 401.
GuestAllowed = Annotated[User | None, Depends(get_optional_user)]
LoggedIn = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_current_admin)]


def ensure_owner_or_admin(user: User, owner_id: int | None) -> None:
    """Проверка доступа к чужому проекту.

    Отдельная функция, а не сравнение в роутере: правило «своё или админ»
    должно звучать одинаково во всех эндпоинтах, иначе его легко забыть
    в одном из них.
    """
    if user.is_admin or owner_id == user.id:
        return
    raise AppError(
        "Проект принадлежит другому пользователю.",
        code="forbidden",
        status_code=403,
    )
