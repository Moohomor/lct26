"""Раскладка, KPI и расписание для визуализации (ТЗ 3.6).

Принцип: бэкенд отдаёт готовую детерминированную картину, фронтенд её
воспроизводит. Никакого случайного поведения «как в жизни»: при одном и том
же `seed` и тех же входных данных результат обязан совпадать до метра и до
секунды — иначе два запуска одного расчёта дадут разные графики, и проверить
результат будет невозможно.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

DEFAULT_SEED = 20260927

#: Размеры полотна по типам объектов, м. Если площадь не задана параметрами
#: объекта, берётся модульная сетка — этого достаточно для плана зала.
DEFAULT_FLOOR = {
    "warehouse": (60.0, 40.0),
    "airport": (120.0, 80.0),
    "medical": (45.0, 30.0),
}

#: Куда робот едет за задачей: координаты в долях от размеров полотна.
ZONE_POSITIONS = {
    "receiving": (0.10, 0.20),
    "storage": (0.55, 0.35),
    "picking": (0.55, 0.75),
    "packing": (0.20, 0.80),
    "shipping": (0.88, 0.30),
    "dispatch": (0.85, 0.65),
    "cleaning": (0.30, 0.50),
    "terminal": (0.70, 0.15),
}

#: Зоны, нужные каждому процессу. Пустой список — рисуем только роботов.
PROCESS_ZONES = {
    "intake": ["receiving", "storage"],
    "storage": ["storage"],
    "picking": ["storage", "picking"],
    "packing": ["packing", "storage"],
    "shipping": ["shipping", "dispatch"],
    "intra_logistics": ["receiving", "storage", "picking", "shipping"],
    "ground_handling": ["receiving", "shipping", "dispatch"],
    "ground_cleaning": ["terminal", "cleaning"],
    "ground_support": ["terminal", "dispatch"],
    "passenger_transport": ["terminal", "cleaning"],
    "sanitation": ["cleaning", "storage"],
    "diagnostics": ["storage", "picking"],
    "ward_logistics": ["storage", "picking", "picking"],
    "lab_logistics": ["receiving", "storage", "picking"],
    "sterile_supply": ["storage", "picking"],
    "medication_delivery": ["storage", "picking"],
}


@dataclass
class SimulationOutcome:
    layout: dict[str, Any]
    kpi: dict[str, Any]
    schedule: dict[str, Any] | None
    duration_ms: int
    notes: list[str] = field(default_factory=list)


def scenario_robots(scenario: Any) -> list[dict[str, Any]]:
    """Состав сценария в виде, который понимает движок имитации.

    Живёт здесь, а не в роутере, потому что список единиц техники нужен и
    пользователю (кнопка «смоделировать»), и генератору демо-проектов. Две
    копии этого списка разошлись бы при первом же изменении полей каталога.
    """
    robots: list[dict[str, Any]] = []
    for line in getattr(scenario, "solutions", ()):
        sol = getattr(line, "solution", None)
        if sol is None or float(line.quantity or 0) <= 0:
            continue
        robots.append(
            {
                "solution_id": str(sol.id),
                "quantity": int(line.quantity),
                "name": sol.name,
                "type_code": sol.solution_type.code if sol.solution_type else None,
                "throughput_per_hour": _opt_float(sol.throughput_per_hour),
                "autonomy_hours": _opt_float(sol.autonomy_hours),
                "battery_capacity_kwh": _opt_float(sol.battery_capacity_kwh),
            }
        )
    return robots


def _floor_size(object_type: str, params: dict[str, Any]) -> tuple[float, float]:
    """Габариты полотна из параметров объекта, с запасным вариантом."""
    length = _num(params, "floor_length_m") or _num(params, "length_m") or _num(params, "area_length_m")
    width = _num(params, "floor_width_m") or _num(params, "width_m") or _num(params, "area_width_m")
    if length and width:
        return float(length), float(width)
    if _num(params, "floor_area_m2"):
        area = float(params["floor_area_m2"])
        ratio = DEFAULT_FLOOR.get(object_type, (1.5, 1.0))
        length = math.sqrt(area * ratio[0] / ratio[1])
        return length, length * ratio[1] / ratio[0]
    return DEFAULT_FLOOR.get(object_type, (60.0, 40.0))


def _opt_float(value: Any) -> float | None:
    """Decimal/None из колонки каталога → float/None для расчёта."""
    return float(value) if value is not None else None


def _num(params: dict[str, Any], code: str) -> float | None:
    value = params.get(code)
    if value in (None, ""):
        return None
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _zones_for(process_codes: list[str]) -> list[str]:
    codes = {c for c in process_codes if c in PROCESS_ZONES}
    if not codes:
        return ["storage", "picking", "shipping"]
    out: list[str] = []
    for code in process_codes:
        for zone in PROCESS_ZONES.get(code, []):
            if zone not in out:
                out.append(zone)
    return out


def simulate_scenario(
    *,
    object_type: str,
    params: dict[str, Any],
    process_codes: list[str],
    robots: list[dict[str, Any]],
    assumptions: Any,
    seed: int | None = None,
    include_schedule: bool = True,
) -> SimulationOutcome:
    """Считает раскладку, KPI и расписание задач.

    Ничего не «крутит»: считается одна картина работы за смену, из которой
    фронтенд собирает анимацию. Так KPI и график не могут разойтись.
    """
    import time

    started = time.perf_counter()
    seed = DEFAULT_SEED if seed is None else int(seed)
    rng = random.Random(seed)
    notes: list[str] = []

    width, depth = _floor_size(object_type, params)
    zone_names = _zones_for(process_codes)

    # ── Зоны ──────────────────────────────────────────────────────────────
    zones = []
    for i, name in enumerate(zone_names):
        fx, fy = ZONE_POSITIONS.get(name, (0.2 + 0.15 * (i % 5), 0.2 + 0.15 * (i // 5)))
        zones.append(
            {
                "code": name,
                "name": _zone_label(name),
                "x": round(fx * width, 2),
                "y": round(fy * depth, 2),
                "w": round(min(14.0, width * 0.16), 2),
                "h": round(min(10.0, depth * 0.18), 2),
            }
        )

    # ── Роботы ────────────────────────────────────────────────────────────
    shift_hours = float(_assump(assumptions, "simulation.shift_hours", 8.0))
    autonomy = float(_assump(assumptions, "simulation.default_autonomy_hours", 8.0))
    charge_share = float(_assump(assumptions, "simulation.charge_share", 0.15))
    load_factor = float(_assump(assumptions, "sizing.load_factor", 0.8))

    units: list[dict[str, Any]] = []
    for entry in robots:
        qty = int(entry.get("quantity") or 1)
        thr = entry.get("throughput_per_hour")
        bat = entry.get("battery_capacity_kwh")
        aut = entry.get("autonomy_hours") or autonomy
        for i in range(qty):
            # Разброс по производительности ±8 %: одинаковые роботы в партии
            # не бывают абсолютно одинаковыми, но разброс небольшой.
            factor = 1.0 + rng.uniform(-0.08, 0.08)
            units.append(
                {
                    "id": f"{entry['solution_id'][:8]}-{i + 1}",
                    "solution_id": entry["solution_id"],
                    "name": entry["name"],
                    "type_code": entry.get("type_code"),
                    "throughput_per_hour": round(float(thr) * factor, 2) if thr else None,
                    "autonomy_hours": round(float(aut), 2),
                    "battery_capacity_kwh": float(bat) if bat else None,
                }
            )

    # ── Парковки и зарядные станции ───────────────────────────────────────
    park_anchor = zones[0] if zones else {"x": 0, "y": 0, "w": 10, "h": 10}
    parking = [
        {
            "id": f"P-{i + 1}",
            "x": round(park_anchor["x"] + (i % 4) * 1.6, 2),
            "y": round(park_anchor["y"] - 4.0 - (i // 4) * 1.4, 2),
            "w": 1.2,
            "h": 0.8,
        }
        for i in range(len(units))
    ]
    stations_count = math.ceil(len(units) / 2) if units else 0
    stations = [
        {
            "id": f"CH-{i + 1}",
            "x": round(park_anchor["x"] - 3.0 - (i % 3) * 1.2, 2),
            "y": round(park_anchor["y"] - 4.0 - (i // 3) * 1.4, 2),
            "w": 0.8,
            "h": 0.6,
            "power_kw": 2.2,
        }
        for i in range(stations_count)
    ]

    # ── Маршруты и расписание ─────────────────────────────────────────────
    schedule: dict[str, Any] | None = None
    tasks_total = 0
    if units and zones and include_schedule:
        schedule = _make_schedule(
            units, zones, shift_hours, rng, load_factor, note=notes
        )
        tasks_total = int(schedule["task_count"])

    # ── KPI ───────────────────────────────────────────────────────────────
    nominal = sum((u["throughput_per_hour"] or 0.0) for u in units)
    # Часть смены уходит на зарядку и переезды: это не «полезная» мощность.
    effective = nominal * shift_hours * load_factor * (1 - charge_share)
    with_data = [u for u in units if u["throughput_per_hour"]]
    kpi: dict[str, Any] = {
        "shift_hours": round(shift_hours, 2),
        "robots": len(units),
        "robots_with_specs": len(with_data),
        "zones": len(zones),
        "charging_stations": len(stations),
        "capacity_per_hour": round(nominal, 1),
        "nominal_capacity_per_shift": round(nominal * shift_hours, 1),
        "effective_capacity_per_shift": round(effective, 1),
        "utilization_pct": round(load_factor * (1 - charge_share) * 100, 1),
        "charge_share_pct": round(charge_share * 100, 1),
        "tasks_total": tasks_total,
        "seed": seed,
        "bottleneck": _bottleneck(units, zones),
    }
    if not with_data:
        kpi["warning"] = (
            "Ни у одного решения не указана производительность: KPI по "
            "пропускной способности не рассчитаны. Заполните ТТХ в каталоге."
        )
        notes.append(kpi["warning"])
    if stations_count * 2 < len(units):
        kpi["charging_warning"] = (
            f"На {len(units)} роботов приходится {stations_count} зарядных станций. "
            "Зарядка станет узким местом смены."
        )
        notes.append(kpi["charging_warning"])

    layout = {
        "object_type": object_type,
        "width_m": round(width, 2),
        "depth_m": round(depth, 2),
        "zones": zones,
        "robots": units,
        "parking": parking,
        "charging_stations": stations,
        "routes": _routes(zones, units),
    }

    return SimulationOutcome(
        layout=layout,
        kpi=kpi,
        schedule=schedule,
        duration_ms=int((time.perf_counter() - started) * 1000),
        notes=notes,
    )


def _assump(assumptions: Any, code: str, default: float) -> float:
    try:
        value = assumptions.float_(code)
        return float(value) if value else default
    except (AttributeError, KeyError, TypeError, ValueError):
        return default


def _zone_label(code: str) -> str:
    return {
        "receiving": "Приёмка",
        "storage": "Склад хранения",
        "picking": "Зона комплектации",
        "packing": "Упаковка",
        "shipping": "Отгрузка",
        "dispatch": "Диспетчерская",
        "cleaning": "Зона уборки",
        "terminal": "Перрон / терминал",
    }.get(code, code)


def _make_schedule(
    units: list[dict[str, Any]],
    zones: list[dict[str, Any]],
    shift_hours: float,
    rng: random.Random,
    load_factor: float,
    *,
    note: list[str],
) -> dict[str, Any]:
    """Распределяет задачи по роботам на смену.

    Расписание строится по зонам в порядке обработки груза: каждая следующая
    точка получает ближайшего свободного робота. Расстояние считается по
    евклидовой метрике плана — для прямоугольного зала это честная оценка
    длины пути.
    """
    for unit in units:
        unit["tasks"] = 0
        unit["distance_m"] = 0.0
        unit["busy_h"] = 0.0
        unit["charge_stops"] = 0

    throughput = max((u["throughput_per_hour"] or 0.0) for u in units) or 1.0
    # Сколько перемещений один робот закрывает за смену: производительность
    # пересчитывается в циклы по типовой длительности цикла.
    per_robot_capacity = max(
        1.0, throughput * shift_hours * load_factor * (60.0 / _CYCLE_MINUTES)
    )

    total_tasks = int(per_robot_capacity * len(units))
    tasks: list[dict[str, Any]] = []
    free_at = {u["id"]: 0.0 for u in units}
    for t in range(total_tasks):
        target = zones[t % len(zones)]
        src = zones[(t - 1) % len(zones)]
        # Берём робота, который освободится раньше всех: если выбирать по
        # расстоянию, роботы выстраиваются в очередь у дальней зоны.
        best = min(units, key=lambda u: (free_at[u["id"]], u["id"]))
        start = free_at[best["id"]]
        dist = _distance(src, target)
        travel_h = dist / _SPEED_MPS / 3600.0
        # Разброс времени обработки ±15 % — иначе все роботы работают в такт.
        service_h = _CYCLE_MINUTES / (60.0 * max(0.2, rng.uniform(0.85, 1.15)))
        tasks.append(
            {
                "id": t + 1,
                "robot_id": best["id"],
                "from": src["code"],
                "to": target["code"],
                "start_h": round(start, 3),
                "duration_h": round(travel_h + service_h, 3),
                "distance_m": round(dist, 1),
                "load": round(rng.uniform(0.4, 1.0), 2),
            }
        )
        best["tasks"] += 1
        best["distance_m"] = round(best["distance_m"] + dist, 1)
        best["busy_h"] = round(best["busy_h"] + travel_h + service_h, 3)
        free_at[best["id"]] = round(start + travel_h + service_h, 3)
        if free_at[best["id"]] > _autonomy_limit(best, shift_hours):
            # Автономности не хватило до конца смены — робот встаёт на зарядку.
            best["charge_stops"] += 1
            charge_h = (
                float(best["battery_capacity_kwh"]) / _CHARGE_KW
                if best["battery_capacity_kwh"]
                else 1.0
            )
            free_at[best["id"]] = round(free_at[best["id"]] + charge_h, 3)

    truncated = len(tasks) > _MAX_TASKS
    if truncated:
        note.append(
            f"Расписание обрезано до {_MAX_TASKS} задач: этого достаточно для "
            "анимации, но не для анализа всего объёма."
        )
    return {
        "tasks": tasks[:_MAX_TASKS],
        "task_count": len(tasks),
        "shift_hours": shift_hours,
        "truncated": truncated,
        "by_robot": [
            {
                "robot_id": u["id"],
                "name": u["name"],
                "tasks": u["tasks"],
                "busy_h": u["busy_h"],
                "distance_m": u["distance_m"],
                "charge_stops": u["charge_stops"],
                "utilization_pct": round(u["busy_h"] / shift_hours * 100, 1) if shift_hours else 0.0,
            }
            for u in units
        ],
    }


#: Константы раскладки. Собраны здесь, а не внутри логики распределения
#: задач, чтобы смена модели имитации не трогала сам алгоритм.
_SPEED_MPS = 1.2
_CYCLE_MINUTES = 6.0
_CHARGE_KW = 2.2
_MAX_TASKS = 2000


def _autonomy_limit(unit: dict[str, Any], shift_hours: float) -> float:
    autonomy = unit.get("autonomy_hours") or shift_hours
    # Последние 20 % автономности оставляем на дорогу до станции.
    return max(0.5, float(autonomy) * 0.8)


def _distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    """Длина пути между центрами зон по плану зала."""
    ax = a.get("x", 0.0) + a.get("w", 0.0) / 2
    ay = a.get("y", 0.0) + a.get("h", 0.0) / 2
    bx = b.get("x", 0.0) + b.get("w", 0.0) / 2
    by = b.get("y", 0.0) + b.get("h", 0.0) / 2
    return math.hypot(ax - bx, ay - by)


def _routes(zones: list[dict[str, Any]], units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Базовые маршруты между зонами — их рисует фоном план зала."""
    if len(zones) < 2:
        return []
    out = []
    for i, a in enumerate(zones):
        b = zones[(i + 1) % len(zones)]
        ax = a["x"] + a["w"] / 2
        ay = a["y"] + a["h"] / 2
        bx = b["x"] + b["w"] / 2
        by = b["y"] + b["h"] / 2
        out.append(
            {
                "from": a["code"],
                "to": b["code"],
                "points": [[round(ax, 2), round(ay, 2)], [round(bx, 2), round(by, 2)]],
                "length_m": round(math.hypot(ax - bx, ay - by), 2),
            }
        )
    return out


def _bottleneck(units: list[dict[str, Any]], zones: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Зона с наименьшей пропускной способностью.

    Определяется по расстоянию до роботов: чем дальше зона от парковок, тем
    больше времени занимает путь. Это же место чаще всего становится причиной
    простоев.
    """
    if not units or not zones:
        return None
    if not any(u.get("throughput_per_hour") for u in units):
        return None
    # Парковки привязаны к первой зоне, поэтому удалённость первой зоны
    # принята за нулевую, остальные считаются от неё.
    base = zones[0]
    worst = min(
        zones,
        key=lambda z: -(abs(z["x"] - base["x"]) + abs(z["y"] - base["y"])),
    )
    return {
        "zone": worst["code"],
        "name": _zone_label(worst["code"]),
        "reason": "самая удалённая зона от парковок: время на перемещение "
        "съедает производительность",
    }
