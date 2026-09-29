"""Иерархический каталог решений (ТЗ 3.3.1): отрасль → объект → процесс →
тип решения → конкретный продукт.

Структура разделена на справочные сущности (processes, solution_types) и
продукт (solutions), чтобы новые продукты добавлялись без изменения схемы.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPrimaryKeyMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.reference import DataSource, ObjectType


class Process(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Процесс объекта, который автоматизируют (ТЗ 3.3.1)."""

    __tablename__ = "processes"
    __table_args__ = (UniqueConstraint("object_type_id", "code", name="uq_process_object_code"),)

    object_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("object_types.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    # ключевой код для подбора и формул (см. services/economics/params.py)
    metric_code: Mapped[str | None] = mapped_column(String(64))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    object_type: Mapped["ObjectType | None"] = relationship()

    solution_types: Mapped[list[SolutionType]] = relationship(
        back_populates="process", cascade="all, delete-orphan", order_by="SolutionType.order_index"
    )


class SolutionType(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Тип роботизированного решения (AMR, FMR, робот-уборщик, AS/RS …)."""

    __tablename__ = "solution_types"
    __table_args__ = (UniqueConstraint("code", name="uq_solution_type_code"),)

    process_id: Mapped[int | None] = mapped_column(
        ForeignKey("processes.id", ondelete="SET NULL"), index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_mobile: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # требует ли оборудование проезда между точками (важно для проверки ширины коридора)
    requires_passage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # максимальная ширина проезда сверх габаритов, м (запас на разминовку)
    passage_margin_m: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=Decimal("0.3"))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    process: Mapped[Process | None] = relationship(back_populates="solution_types")
    solutions: Mapped[list[Solution]] = relationship(back_populates="solution_type")


class Vendor(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Производитель / интегратор."""

    __tablename__ = "vendors"
    __table_args__ = (UniqueConstraint("name", name="uq_vendor_name"),)

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    country: Mapped[str | None] = mapped_column(String(128))
    website: Mapped[str | None] = mapped_column(String(1024))
    region: Mapped[str | None] = mapped_column(String(128))

    solutions: Mapped[list[Solution]] = relationship(back_populates="vendor")


class Solution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Конкретный продукт в каталоге.

    Набор полей соответствует таблице обязательных характеристик ТЗ 3.3.7.
    Незаполненные ТТХ остаются NULL и помечают решение как «данные не
    подтверждены» — по Дополнениям п.4 это допустимо и должно быть видно.
    """

    __tablename__ = "solutions"

    vendor_id: Mapped[int | None] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"), index=True
    )
    solution_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("solution_types.id", ondelete="SET NULL"), index=True
    )

    name: Mapped[str] = mapped_column(String(512), nullable=False)
    catalog_id: Mapped[uuid.UUID | None] = mapped_column(index=True)  # id из CSV организатора
    # operation | piloting | rnd | development
    status: Mapped[str] = mapped_column(String(32), default="operation", index=True, nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(String(128), index=True)
    region: Mapped[str | None] = mapped_column(String(128))
    # Сценарий в выгрузке организатора — перечисление через запятую,
    # у отдельных позиций оно длиннее 255 символов.
    scenario_label: Mapped[str | None] = mapped_column(Text)
    cases: Mapped[str | None] = mapped_column(Text)
    # «Технологическая готовность» 1..9 (колонка УГТ в CSV организатора)
    trl: Mapped[int | None] = mapped_column(Integer)
    market_potential: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))

    # ── Технические характеристики ────────────────────────────────────────
    payload_kg: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    own_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    length_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    width_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    height_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    min_passage_width_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    lift_height_m: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    max_speed_mps: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    throughput_per_hour: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    throughput_unit: Mapped[str | None] = mapped_column(String(32))
    autonomy_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    charge_time_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    positioning_accuracy_mm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    navigation_types: Mapped[list | None] = mapped_column(JSONB)
    min_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    max_temp_c: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    max_noise_dba: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    max_floor_roughness_mm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    # энергетика: сколько кВт нужно на зарядную инфраструктуру
    charge_power_kw: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    # заявленная изготовителем ёмкость АКБ: нужна для стоимости замены батареи
    # и для расчёта энергопотребления
    battery_capacity_kwh: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # ── Экономика ─────────────────────────────────────────────────────────
    # Цена изделия (с НДС, без доставки/ПНР/интеграции)
    unit_price_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    # Откуда взялась цена — без этого расчёт нельзя проверить:
    # catalog — файл организатора; vendor_quote — коммерческое предложение;
    # estimate — оценочное допущение, подлежит уточнению запросом КП.
    price_source: Mapped[str | None] = mapped_column(String(32))
    software_price_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    implementation_price_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    # годовой сервис в % от цены изделия
    service_rate_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    # purchase | lease | raas | service
    purchase_model: Mapped[str] = mapped_column(String(32), default="purchase", nullable=False)
    lifetime_years: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    battery_lifetime_years: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    infrastructure_price_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))

    # ── Применимость и ограничения ────────────────────────────────────────
    applicable_object_types: Mapped[list | None] = mapped_column(JSONB)  # ["warehouse", ...]
    process_codes: Mapped[list | None] = mapped_column(JSONB)  # ["intrawarehouse_logistics", ...]
    restrictions: Mapped[list | None] = mapped_column(JSONB)
    infrastructure_requirements: Mapped[str | None] = mapped_column(Text)
    # требуется ли сертификация для работы в режимных зонах аэропорта
    airside_certified: Mapped[bool | None] = mapped_column(Boolean)
    medical_sanitation_ready: Mapped[bool | None] = mapped_column(Boolean)

    # ── Качество и происхождение данных (ТЗ 3.3.4) ───────────────────────
    # Фотография позиции: путь относительно app/assets. Заполняется из
    # solution_photos.json, который собирается из «Каталога внедрения»
    # ФЦ БАС. Не у всех позиций снимок есть — это нормально.
    photo_file: Mapped[str | None] = mapped_column(String(160), index=True)
    data_source_id: Mapped[int | None] = mapped_column(
        ForeignKey("data_sources.id", ondelete="SET NULL")
    )
    specs_updated_at: Mapped[date | None] = mapped_column(Date)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completeness: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))

    # ── Служебное ─────────────────────────────────────────────────────────
    # Дубли из файла организатора: разные комплектации одного решения (Дополнения п.6)
    is_variant_of_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("solutions.id", ondelete="SET NULL")
    )
    variant_label: Mapped[str | None] = mapped_column(String(128))
    raw: Mapped[dict | None] = mapped_column(JSONB)  # исходная строка CSV без потерь

    vendor: Mapped[Vendor | None] = relationship(back_populates="solutions")
    solution_type: Mapped[SolutionType | None] = relationship(back_populates="solutions")
    data_source: Mapped[DataSource | None] = relationship()

    @property
    def display_name(self) -> str:
        vendor = f"{self.vendor.name} " if self.vendor else ""
        return f"{vendor}{self.name}".strip()

    @property
    def is_data_complete(self) -> bool:
        """Есть ли ключевые ТТХ, без которых подбор и расчёт ненадёжны."""
        return (
            self.payload_kg is not None
            and self.throughput_per_hour is not None
            and self.unit_price_rub is not None
        )
