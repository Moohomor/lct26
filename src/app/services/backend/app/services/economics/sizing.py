"""Расчёт потребного количества оборудования (sizing).

Формула из ТЗ 3.5.2 и раздела «Дополнения»:

    N = D_пик / (Q_ед × K_загрузки × K_готовности)

где D_пик — пиковая часовая потребность в операциях, Q_ед — производительность
единицы оборудования. Коэффициенты берутся из `normatives`, а не из кода,
поэтому администратор может изменить их без правки программы.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SizingResult:
    units: int
    peak_demand: float
    unit_productivity: float
    load_factor: float
    availability: float
    #: запас мощности = units × Q × K_загрузки × K_готовности / D_пик
    capacity_ratio: float
    formula: str
    notes: list[str]

    def as_dict(self) -> dict:
        return {
            "units": self.units,
            "peak_demand": round(self.peak_demand, 2),
            "unit_productivity": round(self.unit_productivity, 2),
            "load_factor": self.load_factor,
            "availability": self.availability,
            "capacity_ratio": round(self.capacity_ratio, 3),
            "formula": self.formula,
            "notes": self.notes,
        }


def required_units(
    *,
    peak_demand: float,
    unit_productivity: float,
    load_factor: float,
    availability: float,
) -> int:
    """Минимальное целое число единиц оборудования."""
    if unit_productivity <= 0 or peak_demand <= 0:
        return 1
    effective = unit_productivity * load_factor * availability
    if effective <= 0:
        return 1
    return max(1, math.ceil(peak_demand / effective))


def size(
    *,
    peak_demand: float,
    unit_productivity: float,
    load_factor: float,
    availability: float,
) -> SizingResult:
    units = required_units(
        peak_demand=peak_demand,
        unit_productivity=unit_productivity,
        load_factor=load_factor,
        availability=availability,
    )
    capacity = units * unit_productivity * load_factor * availability
    ratio = capacity / peak_demand if peak_demand > 0 else 0.0

    notes: list[str] = []
    if 0 < ratio < 1.0:
        notes.append(
            "Расчётная ёмкость меньше пиковой потребности: это невозможно при "
            "целочисленном округлении вверх, проверьте исходные объёмы."
        )
    if 1.0 <= ratio < 1.15:
        notes.append(
            "Запас мощности менее 15 %. Для склада с резервом мощности 15–20 % "
            "стоит добавить одну единицу или пересмотреть пиковый коэффициент."
        )
    elif ratio >= 2.0:
        notes.append(
            "Запас мощности более 100 %: возможно, избыточное количество "
            "оборудования — проверьте, не занижена ли производительность."
        )

    return SizingResult(
        units=units,
        peak_demand=peak_demand,
        unit_productivity=unit_productivity,
        load_factor=load_factor,
        availability=availability,
        capacity_ratio=ratio,
        formula=(
            f"N = ceil({peak_demand:.1f} / ({unit_productivity:.1f} × "
            f"{load_factor:.2f} × {availability:.2f})) = {units}"
        ),
        notes=notes,
    )
