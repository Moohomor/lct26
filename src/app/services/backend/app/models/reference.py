"""Справочники: типы объектов, группы и параметры объекта, источники, нормативы.

Параметры объекта хранятся как данные, а не как колонки (ТЗ 3.2.6):
добавление нового типа объекта или нового поля не требует переработки ядра —
достаточно записи в `parameters`.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPrimaryKeyMixin, TimestampMixin, UUIDPrimaryKeyMixin


class DataSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Источник данных: ТЗ 3.3.4 — ссылка, дата получения, подтверждённость."""

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024))
    kind: Mapped[str] = mapped_column(String(64), default="organizer", nullable=False)
    # organizer | vendor_site | public | assumption
    retrieved_at: Mapped[date | None] = mapped_column(Date)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)


class ObjectType(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Тип объекта: склад, аэропорт, медицинское учреждение."""

    __tablename__ = "object_types"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(64))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    groups: Mapped[list[ParameterGroup]] = relationship(
        back_populates="object_type", cascade="all, delete-orphan", order_by="ParameterGroup.order_index"
    )
    parameters: Mapped[list[Parameter]] = relationship(
        back_populates="object_type", cascade="all, delete-orphan"
    )


class ParameterGroup(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Логическая группа полей формы (в xlsx они помечены строкой «▌ ...»)."""

    __tablename__ = "parameter_groups"
    __table_args__ = (UniqueConstraint("object_type_id", "code", name="uq_pg_object_code"),)

    object_type_id: Mapped[int] = mapped_column(
        ForeignKey("object_types.id", ondelete="CASCADE"), index=True, nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    object_type: Mapped[ObjectType] = relationship(back_populates="groups")
    parameters: Mapped[list[Parameter]] = relationship(
        back_populates="group", cascade="all, delete-orphan", order_by="Parameter.order_index"
    )


class Parameter(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Одно поле объекта: единица измерения, диапазон, значение по умолчанию, источник.

    По этим записям фронтенд собирает форму, а бэкенд валидирует ввод
    (ТЗ 3.2.4, 3.2.5).
    """

    __tablename__ = "parameters"
    __table_args__ = (UniqueConstraint("object_type_id", "code", name="uq_param_object_code"),)

    object_type_id: Mapped[int] = mapped_column(
        ForeignKey("object_types.id", ondelete="CASCADE"), index=True, nullable=False
    )
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("parameter_groups.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64))
    # number | integer | percent | text | enum | bool
    value_type: Mapped[str] = mapped_column(String(32), default="number", nullable=False)
    default_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    default_text: Mapped[str | None] = mapped_column(Text)
    min_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    max_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    # Шаг ввода для ползунков и счётчиков. Держится рядом с диапазоном, а не
    # в интерфейсе: иначе у одного и того же параметра в двух экранах будут
    # разные шаги.
    step: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    # Список строк — подсказки для value_type = "enum" (например, покрытие пола).
    options: Mapped[list[str] | None] = mapped_column(JSONB)
    required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Показывается ли поле в расчёте экономики (ТЗ 3.2.4). Позволяет форме
    # подсветить параметры, от которых зависит итоговая цифра.
    is_affecting_economics: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_demo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Пояснение для поля формы: что означает параметр и как его измерить
    help_text: Mapped[str | None] = mapped_column(Text)
    # «Примечание / источник допущения» из демо-датасета
    note: Mapped[str | None] = mapped_column(Text)
    data_source_id: Mapped[int | None] = mapped_column(ForeignKey("data_sources.id", ondelete="SET NULL"))

    object_type: Mapped[ObjectType] = relationship(back_populates="parameters")
    group: Mapped[ParameterGroup | None] = relationship(back_populates="parameters")
    data_source: Mapped[DataSource | None] = relationship()

    @property
    def default(self) -> object:
        """Значение по умолчанию в виде, пригодном для заполнения формы."""
        if self.value_type == "enum":
            return self.default_text
        if self.value_type == "bool":
            return self.default_text == "Да"
        if self.default_value is not None:
            return float(self.default_value)
        return self.default_text


class Normative(IntPrimaryKeyMixin, TimestampMixin, Base):
    """Версионируемый норматив/допущение расчётной модели (ТЗ 3.5.1, 3.5.8).

    Ни один коэффициент в модели не «зашит» в код: он читается отсюда,
    поэтому у каждого числа есть источник, а администратор может его изменить.
    """

    __tablename__ = "normatives"
    __table_args__ = (UniqueConstraint("code", name="uq_normative_code"),)

    code: Mapped[str] = mapped_column(String(96), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(64), default="общие", nullable=False)
    # Допустимый диапазон правки. Без него администратор может задать
    # отрицательную зарплату или нулевую производительность — и получить
    # расчёт, который нельзя объяснить.
    min_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    max_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    # number | integer | bool | text
    value_type: Mapped[str] = mapped_column(String(32), default="number", nullable=False)
    source: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(32), default="econ-1.0.0", nullable=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Растёт при каждой правке: снимки расчётов ссылаются на версию модели,
    # и по ней видно, каким нормативом посчитаны сохранённые цифры.
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @property
    def as_float(self) -> float:
        return float(self.value)
