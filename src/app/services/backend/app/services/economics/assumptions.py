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
from app.seed.normatives_seed import SCENARIO_RANGES

def _range(normative_code: str, low: float, high: float) -> tuple[str, float, float]:
    """Границы допущения берутся из словаря сценария, а не из диапазонов админки.

    Для большинства параметров это один и тот же норматив, поэтому диапазоны
    совпадают и берутся из одного места. Но множители (стоимость персонала,
    оборудования, объём операций) двигаются в обе стороны — этого требует
    анализ чувствительности (ТЗ 3.5.9), — и «× 0,7» не является опечаткой.
    """
    stored = SCENARIO_RANGES.get(normative_code)
    if stored is not None:
        return normative_code, float(stored[0]), float(stored[1])
    return normative_code, low, high


#: Множители варьируются в обе стороны относительно единицы.
_MULTIPLIER_RANGE: tuple[float, float] = (0.5, 2.0)

SCENARIO_OVERRIDABLE = {
    "labor_cost_multiplier": _range("payroll.multiplier", *_MULTIPLIER_RANGE),
    "equipment_cost_multiplier": ("", *_MULTIPLIER_RANGE),
    "operations_multiplier": ("", *_MULTIPLIER_RANGE),
    "horizon_years": _range("calc.horizon_years", 1, 15),
    "service_rate_pct": _range("opex.service_pct", 0.0, 50.0),
    "discount_rate": _range("finance.discount_rate", 0.0, 1.0),
    "raas_rate_pct": _range("raas.rate_pct_of_capex_per_year", 5.0, 80.0),
    "raas_term_months": _range("raas.term_months", 1, 120),
    "amortization_years": _range("capex.amortization_years", 1, 15),
    "lifetime_years": _range("capex.solution_lifetime_years", 1, 20),
    "battery_lifetime_years": _range("capex.battery_lifetime_years", 1, 10),
    "load_factor": _range("sizing.load_factor", 0.3, 1.0),
    "availability": _range("sizing.availability", 0.5, 1.0),
}


def override_limits() -> dict[str, dict[str, Any]]:
    """Переопределяемые допущения в виде, пригодном для интерфейса.

    `SCENARIO_OVERRIDABLE` намеренно хранит позиционный кортеж: он участвует
    в горячем пути проверки каждого переопределения. Для API он нечитаем —
    кортеж нельзя ни развернуть в JSON как поля, ни сопоставить с кодом
    норматива, по которому этот список и строится.
    """
    return {
        code: {"normative": norm, "min": low, "max": high}
        for code, (norm, low, high) in SCENARIO_OVERRIDABLE.items()
    }


def overrides_by_normative() -> dict[str, list[str]]:
    """Норматив → коды его переопределений.

    Списку допущений нужно знать, какие его строки пользователь вправе
    изменить. Коды в двух словарях не совпадают по названию
    (`payroll.multiplier` против `labor_cost_multiplier`), поэтому связь
    строится явно, а не сравнением строк.
    """
    out: dict[str, list[str]] = {}
    for code, (norm, _low, _high) in SCENARIO_OVERRIDABLE.items():
        if norm:
            out.setdefault(norm, []).append(code)
    return {norm: sorted(codes) for norm, codes in out.items()}


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
