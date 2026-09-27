"""Запуски имитации работы роботов (ТЗ 3.6).

Бэкенд не «крутит» анимацию, а рассчитывает детерминированную раскладку и KPI;
фронтенд только воспроизводит её. Благодаря этому визуализация подтверждает
расчёт, а не украшает его.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPrimaryKeyMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Scenario


class SimulationRun(IntPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "simulation_runs"

    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # queued | running | done | failed
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0..100
    speed_factor: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("1"))
    # 2D-раскладка: зоны, маршруты, точки операций, парковки, зарядные станции
    layout: Mapped[dict | None] = mapped_column(JSONB)
    # KPI: пропускная способность, загрузка, простои, узкие места
    kpi: Mapped[dict | None] = mapped_column(JSONB)
    # расписание задач по роботам для анимации
    schedule: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    scenario: Mapped[Scenario] = relationship()
