"""Загрузка расчётных допущений из таблицы `normatives`.

Все коэффициенты экономики и подбора читаются отсюда. Допущения сценария
(переопределения пользователя) накладываются поверх и помечаются в результате,
чтобы в отчёте было видно, какие числа изменены и на каком основании.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Normative

# Допущения, которые пользователь может переопределить в сценарии,
# и нормативы, к которым их значения по умолчанию.
SCENARIO_OVERRIDABLE = {
    # Множители варьируются в обе стороны: анализ чувствительности по ТЗ
    # требует отклонения и вниз, и вверх от базового значения.
    "labor_cost_multiplier": ("payroll.multiplier", 0.5, 2.0),
    "equipment_cost_multiplier": (None, 0.5, 2.0),
    "operations_multiplier": (None, 0.5, 2.0),
    "horizon_years": ("calc.horizon_years", 1, 15),
    "service_rate_pct": ("opex.service_pct", 0.0, 50.0),
    "discount_rate": ("finance.discount_rate", 0.0, 1.0),
    "raas_rate_pct": ("raas.rate_pct_of_capex_per_year", 5.0, 80.0),
    "raas_term_months": ("raas.term_months", 1, 120),
    "amortization_years": ("capex.amortization_years", 1, 15),
    "lifetime_years": ("capex.solution_lifetime_years", 1, 20),
    "battery_lifetime_years": ("capex.battery_lifetime_years", 1, 10),
    "load_factor": ("sizing.load_factor", 0.3, 1.0),
    "availability": ("sizing.availability", 0.5, 1.0),
}


@dataclass
class Assumptions:
    """Набор действующих допущений с указанием источника каждого значения."""

    values: dict[str, float] = field(default_factory=dict)
    sources: dict[str, str] = field(default_factory=dict)
    overridden: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: float | None = None) -> float:
        if key in self.values:
            return self.values[key]
        if default is not None:
            return default
        raise KeyError(f"Норматив «{key}» не загружен")

    def float_(self, key: str, default: float | None = None) -> float:
        return float(self.get(key, default))

    def as_dict(self) -> dict:
        return {
            "values": {k: round(v, 6) for k, v in sorted(self.values.items())},
            "sources": self.sources,
            "overridden": self.overridden,
        }


def load_assumptions(db: Session, model_version: str) -> Assumptions:
    rows = db.scalars(select(Normative)).all()
    values: dict[str, float] = {}
    sources: dict[str, str] = {}
    for row in rows:
        values[row.code] = float(row.value)
        sources[row.code] = row.source or "не указан"
    return Assumptions(values=values, sources=sources)


def apply_overrides(assumptions: Assumptions, overrides: dict | None) -> Assumptions:
    """Накладывает допущения сценария, проверяя допустимые границы."""
    if not overrides:
        return assumptions
    for key, value in overrides.items():
        if key not in SCENARIO_OVERRIDABLE:
            raise AppError(
                f"Допущение «{key}» неизвестно.",
                code="unknown_assumption",
                hint="Список допустимых допущений сценария — в разделе «Допущения».",
                details={"allowed": sorted(SCENARIO_OVERRIDABLE)},
            )
        _norm_code, low, high = SCENARIO_OVERRIDABLE[key]
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            raise AppError(
                f"Допущение «{key}» должно быть числом.",
                code="invalid_assumption",
            ) from None
        if not (low <= numeric <= high):
            raise AppError(
                f"Значение допущения «{key}» вне допустимого диапазона.",
                code="assumption_out_of_range",
                details={"value": numeric, "min": low, "max": high},
            )
        assumptions.values[key] = numeric
        assumptions.sources[key] = "допущение сценария (пользователь)"
        assumptions.overridden[key] = value
    return assumptions


def describe(assumptions: Assumptions) -> list[dict]:
    """Список допущений для интерфейса: имя, значение, единица, источник."""
    out: list[dict] = []
    for code, source in sorted(assumptions.sources.items()):
        out.append(
            {
                "code": code,
                "value": round(assumptions.values[code], 6),
                "source": source,
                "is_override": code in assumptions.overridden
                or any(k == code for k in assumptions.overridden),
            }
        )
    return out


def default_for(key: str) -> Decimal | None:
    return None
