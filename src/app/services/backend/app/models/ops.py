"""Служебные таблицы: журнал импортов, аудит, версия каталога."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPrimaryKeyMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.project import Scenario
    from app.models.user import User


class ImportBatch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Журнал загрузки данных: что, откуда и с каким результатом загружено.

    ТЗ 3.3.6 / 4.2.7: конкурсная версия работает на заранее загруженных данных,
    а по каждому загруженному факту видно происхождение.
    """

    __tablename__ = "import_batches"

    # catalog_csv | object_params | reference_solutions
    kind: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_file: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="done", nullable=False)
    created_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    # предупреждения: дубли, пустые поля, неизвестные типы
    warnings: Mapped[list | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))


class CatalogVersion(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Версия состояния каталога — попадает в каждый расчёт (ТЗ 3.1.5)."""

    __tablename__ = "catalog_versions"

    version: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    solutions_count: Mapped[int] = mapped_column(Integer, default=0)
    is_current: Mapped[bool] = mapped_column(default=False, nullable=False)
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL")
    )
    note: Mapped[str | None] = mapped_column(Text)


class AuditLog(IntPrimaryKeyMixin, Base):
    """Кто и что менял в каталоге/справочниках/нормативах (ТЗ 3.1.4)."""

    __tablename__ = "audit_log"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User | None] = relationship()
