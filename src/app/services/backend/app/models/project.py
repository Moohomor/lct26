"""Проекты, сценарии и сохранённые результаты расчётов."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPrimaryKeyMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.catalog import Solution
    from app.models.reference import ObjectType
    from app.models.user import User


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Проект пользователя: тип объекта + параметры + набор решений."""

    __tablename__ = "projects"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    object_type_id: Mapped[int] = mapped_column(
        ForeignKey("object_types.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    organization: Mapped[str | None] = mapped_column(String(255))
    # draft | in_progress | calculated | archived
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True, nullable=False)
    # {"<code параметра>": значение} — форма и импорт пишут сюда
    parameters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    # процессы объекта, выбранные для роботизации: они определяют требования
    # к решениям и состав базового сценария
    process_codes: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    # версия справочника параметров на момент заполнения (воспроизводимость, ТЗ 3.1.5)
    params_version: Mapped[str | None] = mapped_column(String(32))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_file_name: Mapped[str | None] = mapped_column(String(512))
    uploaded_file_path: Mapped[str | None] = mapped_column(String(1024))

    user: Mapped[User] = relationship()
    object_type: Mapped[ObjectType] = relationship()
    solutions: Mapped[list[ProjectSolution]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    scenarios: Mapped[list[Scenario]] = relationship(
        back_populates="project", cascade="all, delete-orphan", order_by="Scenario.order_index"
    )


class ProjectSolution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Решение в подборке проекта.

    ТЗ 3.4.4: решение можно добавить вручную, даже если оно не попало в
    автоматическую подборку, — тогда заполняем `warning`.
    """

    __tablename__ = "project_solutions"
    __table_args__ = (
        UniqueConstraint("project_id", "solution_id", name="uq_project_solution"),
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    solution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("solutions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    added_manually: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    warning: Mapped[str | None] = mapped_column(Text)
    # снимок результата подбора на момент добавления
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    match_reasons: Mapped[dict | None] = mapped_column(JSONB)

    project: Mapped[Project] = relationship(back_populates="solutions")
    solution: Mapped[Solution] = relationship()


class Scenario(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Сценарий расчёта: без роботизации / покупка / роботы как услуга (ТЗ 3.5.5)."""

    __tablename__ = "scenarios"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # baseline | purchase | raas
    kind: Mapped[str] = mapped_column(String(32), default="purchase", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # переопределения допущений пользователем (ТЗ 3.5.3, 3.5.4)
    assumptions: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    horizon_years: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_calculated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=None
    )

    project: Mapped[Project] = relationship(back_populates="scenarios")
    solutions: Mapped[list[ScenarioSolution]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )
    calculations: Mapped[list[Calculation]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan", order_by="Calculation.id.desc()"
    )


class ScenarioSolution(IntPrimaryKeyMixin, Base):
    """Состав оборудования сценария."""

    __tablename__ = "scenario_solutions"
    __table_args__ = (
        UniqueConstraint("scenario_id", "solution_id", name="uq_scenario_solution"),
    )

    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    solution_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("solutions.id", ondelete="CASCADE"), nullable=False
    )
    # сколько единиц нужно по расчёту sizing
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1"))
    # количество, зафиксированное пользователем: sizing не имеет права
    # пересчитывать то, что человек осознанно задал руками
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    scenario: Mapped[Scenario] = relationship(back_populates="solutions")
    solution: Mapped[Solution] = relationship()


class Calculation(IntPrimaryKeyMixin, Base):
    """Снимок расчёта: вход + результат + версии (ТЗ 3.1.5, 3.5.8).

    Хранится снимок, а не только «последний результат», чтобы расчёт можно
    было воспроизвести позже — даже после правки нормативов и каталога.
    """

    __tablename__ = "calculations"

    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    # Дублируют ключевые цифры из `result`, чтобы список расчётов не требовал
    # распаковки JSONB для каждой строки. `result` остаётся источником истины.
    kind: Mapped[str] = mapped_column(String(32), default="purchase", nullable=False)
    model_version: Mapped[str] = mapped_column(String(32), nullable=False)
    catalog_version: Mapped[str | None] = mapped_column(String(64))
    params_version: Mapped[str | None] = mapped_column(String(32))
    capex_total: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    annual_effect: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    payback_years: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    input_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    scenario: Mapped[Scenario] = relationship(back_populates="calculations")
