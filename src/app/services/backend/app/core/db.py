"""Подключение к БД: движок, фабрика сессий, fastapi-зависимость."""

from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, literal, or_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base  # noqa: F401  (реэкспорт для скриптов)

engine = create_engine(
    settings.sqlalchemy_url,
    echo=settings.db_echo,
    pool_pre_ping=True,  # спасает от "server closed the connection unexpectedly"
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def jsonb_contains(column: Any, values: list[str]) -> Any:
    """Условие «JSONB-массив содержит хотя бы один из кодов».

    Правая часть привязывается как Python-список, а не как готовая строка.
    Разница неочевидна и опасна: если передать json.dumps(["warehouse"])
    с типом JSONB, psycopg сериализует строку ещё раз, в PostgreSQL попадёт
    JSON-скаляр, и `array @> scalar` вернёт false — молча, без исключения.
    Фильтр по типу объекта просто перестаёт что-либо находить.
    """
    if not values:
        # Пустой список кодов означает «не фильтровать», а не «ничего не подходит».
        return None
    clauses = [column.op("@>")(literal([v], JSONB)) for v in values]
    if len(clauses) == 1:
        return clauses[0]
    return or_(*clauses)


def jsonb_empty(column: Any) -> Any:
    """Условие «колонка не заполнена»: NULL либо пустой массив.

    Отсутствие разметки и явный пустой список означают одно и то же — решение
    не привязано к конкретным типам объекта.
    """
    return or_(column.is_(None), column == literal([], JSONB))


def get_db() -> Iterator[Session]:
    """Зависимость FastAPI: одна сессия на запрос."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
