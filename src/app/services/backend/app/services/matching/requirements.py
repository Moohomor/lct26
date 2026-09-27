"""Требования объекта к роботизированному решению.

Подбор невозможно сделать «по похожему названию»: нужно знать, какие
конкретные величины робот обязан обеспечить на объекте. Этот модуль переводит
заполненную форму проекта в список проверяемых требований, а движок
подбора (engine.py) проверяет по ним каждое решение.

Каждое требование помнит, из какого параметра проекта оно получено, —
чтобы интерфейс мог показать пользователю не «решение не подходит», а
«решение не подходит: ширина рабочего прохода 1,5 м уже минимальной
допустимой 1,95 м».
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.services.importers.catalog_taxonomy import PROCESSES

Severity = Literal["blocker", "warning", "info"]
Comparator = Literal["min", "max", "range", "eq", "one_of"]


@dataclass(frozen=True)
class Requirement:
    """Одно проверяемое условие применимости."""

    code: str
    label: str
    severity: Severity
    #: минимально допустимое значение решения
    minimum: float | None = None
    #: максимально допустимое значение решения
    maximum: float | None = None
    unit: str | None = None
    #: откуда взялось требование — код параметра проекта
    source_param: str | None = None
    #: текст требования для показа пользователю
    text: str = ""
    #: значения, при которых требование неприменимо (например, «нет»)
    skip_if: tuple[str, ...] = field(default=())

    def format_text(self, params: dict) -> str:
        if self.text:
            return self.text
        parts = []
        if self.minimum is not None:
            parts.append(f"не менее {self.minimum:g} {self.unit or ''}".strip())
        if self.maximum is not None:
            parts.append(f"не более {self.maximum:g} {self.unit or ''}".strip())
        return f"{self.label}: {', '.join(parts)}" if parts else self.label


def _num(params: dict, code: str) -> float | None:
    value = params.get(code)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _txt(params: dict, code: str) -> str:
    value = params.get(code)
    return str(value).strip().lower() if value not in (None, "") else ""


def _is_no(params: dict, code: str) -> bool:
    """Ответ «нет» на вопрос о наличии системы/возможности."""
    return _txt(params, code) in {"нет", "no", "false", "0", "отсутствует", "не имеется"}


def _fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


# ─────────────────────────────────────────────────────────────────────────────
# Общие для всех объектов требования
# ─────────────────────────────────────────────────────────────────────────────


def _requirement_payload(params: dict, needed_kg: float | None, source: str, label: str) -> Requirement | None:
    if needed_kg is None or needed_kg <= 0:
        return None
    return Requirement(
        code="payload",
        label=label,
        severity="blocker",
        minimum=needed_kg,
        unit="кг",
        source_param=source,
        text=f"Грузоподъёмность не менее {_fmt(needed_kg, 0)} кг",
    )


def _requirement_passage(params: dict, width_param: str, margin: float) -> Requirement | None:
    width = _num(params, width_param)
    if width is None:
        return None
    return Requirement(
        code="passage",
        label="Ширина проезда",
        severity="blocker",
        maximum=width,
        unit="м",
        source_param=width_param,
        text=(
            f"Габарит проезда с запасом {margin:g} м должен укладываться "
            f"в доступную ширину {_fmt(width)} м"
        ),
    )


def _requirement_floor(params: dict) -> Requirement | None:
    roughness = _num(params, "floor_roughness_mm")
    if roughness is None:
        return None
    return Requirement(
        code="floor_roughness",
        label="Ровность пола",
        severity="blocker",
        maximum=roughness,
        unit="мм",
        source_param="floor_roughness_mm",
        text=f"Допустимое отклонение пола не более {_fmt(roughness)} мм",
    )


def _requirement_temp(params: dict) -> Requirement | None:
    low = _num(params, "min_temp_c")
    if low is None:
        return None
    return Requirement(
        code="temperature",
        label="Температура эксплуатации",
        severity="blocker",
        minimum=low,
        unit="°C",
        source_param="min_temp_c",
        text=f"Решение должно работать при температуре не выше {_fmt(low, 0)} °C",
    )


def _requirement_noise(params: dict) -> Requirement | None:
    limit = _num(params, "noise_limit_dba")
    if limit is None:
        return None
    return Requirement(
        code="noise",
        label="Уровень шума",
        severity="warning",
        maximum=limit,
        unit="дБА",
        source_param="noise_limit_dba",
        text=(
            f"Если уровень шума решения не подтверждён, требуется согласование: "
            f"предел {_fmt(limit, 0)} дБА"
        ),
    )


def _requirement_power(params: dict) -> Requirement | None:
    available = _num(params, "power_available_kw")
    if available is None:
        return None
    return Requirement(
        code="power",
        label="Электропитание зарядной инфраструктуры",
        severity="info",
        minimum=available,
        unit="кВт",
        source_param="power_available_kw",
        text=f"Доступно {_fmt(available, 0)} кВт под зарядную инфраструктуру",
    )


def _requirement_autonomy(params: dict) -> Requirement | None:
    """Робот должен пережить смену либо иметь станцию подзарядки."""
    shift = _num(params, "shift_hours") or _num(params, "medical_shifts_day")
    if shift is None or shift <= 0:
        return None
    return Requirement(
        code="autonomy",
        label="Автономность",
        severity="info",
        minimum=shift * 0.5,
        unit="ч",
        source_param="shift_hours",
        text=(
            f"Продолжительность смены {_fmt(shift, 0)} ч: автономность желательна "
            f"не менее {_fmt(shift * 0.5, 1)} ч либо нужна зарядная станция"
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Склад
# ─────────────────────────────────────────────────────────────────────────────


def warehouse_requirements(object_type: str, process_code: str, params: dict) -> list[Requirement]:
    reqs: list[Requirement] = []

    if process_code in {"intra_logistics", "receiving", "shipping", "storage"}:
        req = _requirement_payload(params, _num(params, "pallet_weight_kg"), "pallet_weight_kg", "Грузоподъёмность (паллета)")
        if req:
            reqs.append(req)
        width_param = "main_aisle_width_m"
    elif process_code in {"picking", "sorting"}:
        req = _requirement_payload(params, _num(params, "item_weight_kg"), "item_weight_kg", "Грузоподъёмность (штучный груз)")
        if req:
            reqs.append(req)
        width_param = "work_aisle_width_m"
    else:
        width_param = "main_aisle_width_m"

    passage = _requirement_passage(params, width_param, 0.3)
    if passage:
        reqs.append(passage)

    floor = _requirement_floor(params)
    if floor:
        reqs.append(floor)

    # Стеллажи выше одного уровня требуют решения с подъёмом груза.
    if process_code == "storage":
        positions = _num(params, "pallet_positions")
        if positions and positions > 0 and not _is_no(params, "has_wms"):
            reqs.append(
                Requirement(
                    code="multilevel",
                    label="Многоуровневое хранение",
                    severity="info",
                    source_param="racking_system",
                    text="Для многоуровневого хранения нужен робот с подъёмным устройством или AS/RS",
                )
            )

    if _is_no(params, "has_wms"):
        reqs.append(
            Requirement(
                code="wms",
                label="Интеграция с WMS",
                severity="warning",
                source_param="has_wms",
                text="На объекте нет WMS: закладывайте интеграцию и обмен данными в CAPEX",
            )
        )
    if _is_no(params, "has_erp"):
        reqs.append(
            Requirement(
                code="erp",
                label="Интеграция с учётной системой",
                severity="info",
                source_param="has_erp",
                text="Учётная система не указана: подтвердите требования к обмену данными",
            )
        )

    autonomy = _requirement_autonomy(params)
    if autonomy:
        reqs.append(autonomy)
    power = _requirement_power(params)
    if power:
        reqs.append(power)
    return reqs


def warehouse_peak_demand(object_type: str, process_code: str, params: dict) -> float | None:
    """Пиковая потребность в единицах обработки в сутки для sizing."""
    peak = _num(params, "peak_factor") or 1.0
    shift_hours = _num(params, "shift_hours") or 11.0
    shifts = _num(params, "shifts_per_day") or 1.0

    if process_code in {"receiving", "intra_logistics", "shipping"}:
        inbound = _num(params, "inbound_pallets_day") or 0.0
        outbound = _num(params, "outbound_pallets_day") or 0.0
        return (inbound + outbound) * peak / max(shifts * shift_hours, 1e-6)
    if process_code == "picking":
        return (_num(params, "picking_lines_day") or 0.0) * peak / max(shifts * shift_hours, 1e-6)
    if process_code == "sorting":
        return (_num(params, "picking_units_day") or 0.0) * peak / max(shifts * shift_hours, 1e-6)
    if process_code == "cleaning":
        area = _num(params, "active_area_m2") or _num(params, "total_area_m2")
        return area / max(shifts * shift_hours, 1e-6) if area else None
    return None


def warehouse_demand_unit(process_code: str) -> str:
    return {
        "picking": "строк/ч",
        "sorting": "шт/ч",
        "cleaning": "м²/ч",
    }.get(process_code, "паллет/ч")


# ─────────────────────────────────────────────────────────────────────────────
# Аэропорт
# ─────────────────────────────────────────────────────────────────────────────


def airport_requirements(object_type: str, process_code: str, params: dict) -> list[Requirement]:
    reqs: list[Requirement] = []

    if process_code == "baggage":
        # Тележка на перроне везёт не один чемодан, а партию: считаем
        # номинальную загрузку тележки как 20 единиц багажа.
        unit_weight = _num(params, "baggage_weight_kg")
        if unit_weight:
            req = _requirement_payload(
                params, unit_weight * 20, "baggage_weight_kg", "Грузоподъёмность (партия багажа)"
            )
            if req:
                req.text = (
                    f"Грузоподъёмность не менее {_fmt(unit_weight * 20, 0)} кг "
                    f"(20 единиц багажа по {_fmt(unit_weight, 1)} кг)"
                )
                reqs.append(req)
    elif process_code == "ground_handling":
        unit_weight = _num(params, "baggage_weight_kg")
        if unit_weight:
            req = _requirement_payload(
                params, unit_weight * 20, "baggage_weight_kg", "Тяговые возможности"
            )
            if req:
                req.label = "Буксируемая масса"
                req.text = (
                    "Решение должно буксировать тележки с партией багажа "
                    f"(не менее {_fmt(unit_weight * 20, 0)} кг)"
                )
                reqs.append(req)
    elif process_code == "ground_cleaning":
        noise = _requirement_noise(params)
        if noise:
            reqs.append(noise)
    elif process_code in {"catering", "terminal_logistics"}:
        meals = _num(params, "onboard_meals_day")
        if meals:
            req = _requirement_payload(params, meals / 200, "onboard_meals_day", "Грузоподъёмность (норма партии)")
            if req:
                req.text = (
                    f"Норма парции — {_fmt(meals / 200, 0)} порций на рейс "
                    f"({_fmt(meals, 0)} порций в сутки)"
                )
                reqs.append(req)

    temp = _requirement_temp(params)
    if temp and process_code in {"ground_handling", "ground_cleaning", "waste"}:
        reqs.append(temp)

    if process_code in {"ground_handling", "baggage", "terminal_logistics"}:
        cert_text = _txt(params, "airside_cert_required")
        if cert_text and "нет" not in cert_text and "не треб" not in cert_text:
            reqs.append(
                Requirement(
                    code="airside_cert",
                    label="Допуск к работам в режимных зонах",
                    severity="blocker",
                    source_param="airside_cert_required",
                    text="Оборудование для перрона должно иметь допуск к работам в режимных зонах аэродрома",
                )
            )
        zones = _num(params, "security_zones")
        if zones and zones > 1:
            reqs.append(
                Requirement(
                    code="security_zones",
                    label="Режимные зоны",
                    severity="warning",
                    source_param="security_zones",
                    text=(
                        f"Объект разделён на {zones:.0f} режимных зон: требуется "
                        "управление пересечением зон и разграничение доступа"
                    ),
                )
            )

    if _is_no(params, "has_fids"):
        reqs.append(
            Requirement(
                code="fids",
                label="Интеграция с FIDS/AODB",
                severity="warning",
                source_param="has_fids",
                text="Система FIDS/AODB не указана: интеграция с ней потребует отдельной проработки",
            )
        )

    autonomy = _requirement_autonomy(params)
    if autonomy:
        reqs.append(autonomy)
    power = _requirement_power(params)
    if power:
        reqs.append(power)
    return reqs


def airport_peak_demand(object_type: str, process_code: str, params: dict) -> float | None:
    peak = _num(params, "peak_factor")
    if process_code == "baggage":
        base = _num(params, "baggage_units_day")
    elif process_code == "ground_handling":
        base = ((_num(params, "flights_day") or 0.0) * (_num(params, "gse_ops_per_flight") or 1.0))
    elif process_code == "ground_cleaning":
        base = _num(params, "cleaning_area_m2")
    elif process_code == "catering":
        base = _num(params, "onboard_meals_day")
    elif process_code == "terminal_logistics":
        base = _num(params, "internal_tug_runs_day")
    else:
        base = None
    if not base:
        return None
    return base * (peak or 1.0) / 24.0


def airport_demand_unit(process_code: str) -> str:
    return {
        "ground_cleaning": "м²/ч",
        "catering": "порций/ч",
    }.get(process_code, "ед./ч")


# ─────────────────────────────────────────────────────────────────────────────
# Медицинское учреждение
# ─────────────────────────────────────────────────────────────────────────────


def medical_requirements(object_type: str, process_code: str, params: dict) -> list[Requirement]:
    reqs: list[Requirement] = []

    if process_code == "meals":
        # Тележка с питанием на несколько пациентов — это основная нагрузка.
        req = _requirement_payload(
            params, _num(params, "meal_trolley_weight_kg"), "meal_trolley_weight_kg", "Грузоподъёмность (тележка с питанием)"
        )
        if req:
            reqs.append(req)
    elif process_code in {"meds", "lab"}:
        req = _requirement_payload(params, _num(params, "item_weight_kg"), "item_weight_kg", "Грузоподъёмность (груз)")
        if req:
            reqs.append(req)
    elif process_code == "linen":
        req = _requirement_payload(
            params, _num(params, "linen_container_kg"), "linen_container_kg", "Грузоподъёмность (контейнер с бельём)"
        )
        if req:
            reqs.append(req)
    elif process_code == "waste":
        req = _requirement_payload(
            params, _num(params, "waste_b_kg_day"), "waste_b_kg_day", "Грузоподъёмность (контейнер с отходами)"
        )
        if req:
            req.text = (
                "Контейнер с отходами класса Б тяжёлый: требуется решение "
                "с достаточной грузоподъёмностью и герметичным баком"
            )
            reqs.append(req)

    corridor = _requirement_passage(params, "corridor_width_m", 0.2)
    if corridor:
        # В больнице критичнее всего: нельзя застрять в коридоре.
        corridor.severity = "blocker"
        reqs.append(corridor)

    noise = _requirement_noise(params)
    if noise:
        reqs.append(noise)

    floors = _num(params, "floors_count")
    if floors and floors > 1:
        if _is_no(params, "has_elevator_api"):
            reqs.append(
                Requirement(
                    code="multifloor",
                    label="Межэтажное перемещение",
                    severity="blocker",
                    source_param="floors_count",
                    text=(
                        f"В здании {floors:.0f} этажа, а интеграция с лифтами не указана: "
                        "межэтажная доставка потребует лифта или пандуса"
                    ),
                )
            )
        else:
            reqs.append(
                Requirement(
                    code="multifloor",
                    label="Межэтажное перемещение",
                    severity="warning",
                    source_param="floors_count",
                    text=f"В здании {floors:.0f} этажа: потребуется интеграция с лифтами",
                )
            )

    disinfection = _txt(params, "disinfection_required")
    if disinfection and "нет" not in disinfection and "не треб" not in disinfection:
        reqs.append(
            Requirement(
                code="sanitation",
                label="Санитарная обработка",
                severity="blocker",
                source_param="disinfection_required",
                text="Оборудование должно допускать дезинфекцию между рейсами",
            )
        )

    surface = _txt(params, "surface_requirement")
    if surface:
        reqs.append(
            Requirement(
                code="surface",
                label="Материал поверхностей",
                severity="info",
                source_param="surface_requirement",
                text=f"Требования к поверхностям: {surface}",
            )
        )

    for code, label, param in (
        ("mis", "Интеграция с МИС", "has_mis"),
        ("lis", "Интеграция с ЛИС", "has_lis"),
    ):
        if _is_no(params, param):
            reqs.append(
                Requirement(
                    code=code,
                    label=label,
                    severity="warning",
                    source_param=param,
                    text=f"{label} на объекте не указана: заложите интеграцию в CAPEX",
                )
            )

    autonomy = _requirement_autonomy(params)
    if autonomy:
        reqs.append(autonomy)
    power = _requirement_power(params)
    if power:
        reqs.append(power)
    return reqs


def medical_peak_demand(object_type: str, process_code: str, params: dict) -> float | None:
    if process_code == "meals":
        base = _num(params, "meals_total_day")
        per = _num(params, "meals_per_day") or 1.0
        runs = base / per if (base and per) else None
    elif process_code == "linen":
        dirty = _num(params, "dirty_linen_kg_day")
        container = _num(params, "linen_container_kg") or 30.0
        runs = (dirty / container) if dirty else None
    elif process_code == "meds":
        base = _num(params, "med_orders_day")
        stat = (_num(params, "stat_share_pct") or 0.0) / 100
        runs = base * (1 + stat) if base else None
    elif process_code == "lab":
        base = _num(params, "samples_day")
        runs = base * 2 if base else None  # проба туда, результат обратно
    elif process_code == "waste":
        waste = (_num(params, "waste_a_kg_day") or 0) + (_num(params, "waste_b_kg_day") or 0)
        per_day = _num(params, "waste_removal_per_day") or 1.0
        runs = (waste / 30.0) * per_day if waste else None
    elif process_code == "supplies":
        runs = _num(params, "supplies_runs_day")
    else:
        runs = None
    if not runs:
        return None
    # Работа идёт круглосуточно, но пик приходится на несколько часов в сутки.
    return runs * (_num(params, "peak_factor") or 1.0) / 8.0


def medical_demand_unit(process_code: str) -> str:
    return "рейсов/ч"


BUILDERS = {
    "warehouse": (warehouse_requirements, warehouse_peak_demand, warehouse_demand_unit),
    "airport": (airport_requirements, airport_peak_demand, airport_demand_unit),
    "medical": (medical_requirements, medical_peak_demand, medical_demand_unit),
}


def process_metric_code(object_type: str, process_code: str) -> str | None:
    for proc in PROCESSES:
        if proc.object_type == object_type and proc.code == process_code:
            return proc.metric_code
    return None


def build_requirements(
    object_type: str, process_code: str, params: dict
) -> tuple[list[Requirement], float | None, str]:
    """Требования, пиковая потребность и единица измерения для процесса."""
    requirements_fn, demand_fn, unit_fn = BUILDERS[object_type]
    reqs = requirements_fn(object_type, process_code, params)
    # Общие для всех объектов ограничения добавляем один раз.
    if not any(r.code == "power" for r in reqs):
        power = _requirement_power(params)
        if power:
            reqs.append(power)
    return reqs, demand_fn(object_type, process_code, params), unit_fn(process_code)
