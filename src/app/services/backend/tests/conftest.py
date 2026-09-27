"""Общие приспособления для тестов.

Тесты работают с настоящей базой, а не с заглушками: подменять движок
подбора или экономику в тестах значило бы проверять не то, что работает
у пользователя. Поэтому фикстуры поднимают приложение и прокидывают в него
запросы через TestClient — тот же путь, что и у браузера.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

# backend/app/tests/conftest.py → backend
BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Корень проекта содержит одноимённый пакет `app` (src/app — заглушка для
# фронтенда). pytest при старте вставляет его родительский каталог в sys.path
# и импортирует `app` до загрузки нашего conftest — после этого `import app`
# находит не тот пакет, и тесты падают с ModuleNotFoundError. Поэтому
# неверно импортированный модуль удаляется, чтобы следующий импорт нашёл
# backend/app.
for _name in [n for n in sys.modules if n == "app" or n.startswith("app.")]:
    _module = sys.modules[_name]
    _path = getattr(_module, "__file__", "") or ""
    if "services/backend" not in _path:
        del sys.modules[_name]

# База для тестов — отдельная, чтобы прогон не зависел от того, что лежит
# в рабочей. Переопределяется переменной окружения TEST_DATABASE_URL.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://root:123456@localhost:5432/robotics_test",
)


@pytest.fixture(scope="session")
def client():
    """HTTP-клиент приложения с загруженными данными организатора."""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.seed.seed import is_seeded

    from app.core.db import SessionLocal

    db = SessionLocal()
    try:
        if not is_seeded(db):
            pytest.skip("Данные организатора не загружены: выполните `db seed`")
    finally:
        db.close()

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def user_headers(client) -> dict[str, str]:
    """Токен обычного пользователя: регистрация и вход на каждый тест."""
    email = f"test-{os.getpid()}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "test12345", "full_name": "Тест"},
    )
    tokens = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "test12345"}
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture()
def admin_headers(client) -> dict[str, str]:
    """Токен демо-администратора."""
    tokens = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "demo12345"},
    ).json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture()
def db_session() -> Iterator:
    """Сессия БД для тестов, которым нужен прямой доступ к моделям."""
    from app.core.db import SessionLocal

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
