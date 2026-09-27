"""Аутентификация: регистрация, вход, обновление токена, профиль (ТЗ 3.1.1).

Гость — это отсутствие токена: отдельной записи в таблице `users` у него нет,
и все справочники для него доступны без авторизации.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlalchemy import func, select

from app.core.config import settings
from app.core.deps import DbSession, LoggedIn
from app.core.errors import AppError
from app.core.security import (
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import Calculation, Project, User
from app.schemas.api import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


def _issue_tokens(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.access_token_ttl_minutes * 60,
        user=UserOut.model_validate(user),
    )


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> TokenPair:
    email = payload.email.lower().strip()
    exists = db.scalar(select(User.id).where(func.lower(User.email) == email))
    if exists is not None:
        raise AppError(
            "Пользователь с такой почтой уже зарегистрирован.",
            code="email_taken",
            hint="Попробуйте войти или восстановить пароль.",
            status_code=status.HTTP_409_CONFLICT,
        )
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        organization=payload.organization,
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_tokens(user)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: DbSession) -> TokenPair:
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    # Одинаковый ответ для «нет такого e-mail» и «неверный пароль»: иначе
    # форма входа превращается в способ узнать, какие адреса зарегистрированы.
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(
            "Неверная почта или пароль.",
            code="invalid_credentials",
            hint="Проверьте адрес и раскладку клавиатуры — пароль чувствителен к регистру.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    if not user.is_active:
        raise AppError(
            "Учётная запись отключена.",
            code="account_disabled",
            hint="Обратитесь к администратору платформы.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    user.last_login_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)
    return _issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    claims = decode_token(payload.refresh_token, TOKEN_TYPE_REFRESH)
    if claims is None:
        raise AppError(
            "Токен обновления недействителен или истёк.",
            code="invalid_token",
            hint="Войдите заново.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    subject = claims.get("sub")
    user = db.get(User, int(subject)) if str(subject).isdigit() else None
    if user is None or not user.is_active:
        raise AppError(
            "Пользователь не найден или отключён.",
            code="invalid_token",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return _issue_tokens(user)


@router.get("/me", response_model=UserOut)
def me(user: LoggedIn) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChangeRequest, user: LoggedIn, db: DbSession) -> None:
    if not verify_password(payload.old_password, user.password_hash):
        raise AppError(
            "Текущий пароль указан неверно.",
            code="invalid_credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user.password_hash = hash_password(payload.new_password)
    db.commit()


@router.get("/me/summary")
def my_summary(user: LoggedIn, db: DbSession) -> dict:
    """Сводка для личного кабинета: сколько проектов, расчётов и решений."""
    project_count = db.scalar(
        select(func.count()).select_from(Project).where(Project.user_id == user.id)
    )
    calculation_count = db.scalar(
        select(func.count())
        .select_from(Calculation)
        .where(Calculation.user_id == user.id)
    )
    solved = db.scalar(
        select(func.count())
        .select_from(Calculation)
        .where(Calculation.user_id == user.id, Calculation.payback_years.isnot(None))
    )
    return {
        "user": UserOut.model_validate(user).model_dump(mode="json"),
        "project_count": project_count or 0,
        "calculation_count": calculation_count or 0,
        "projects_with_payback": solved or 0,
    }
