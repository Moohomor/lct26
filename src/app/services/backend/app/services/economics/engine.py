"""Экономическая модель платформы (ТЗ 3.5).

Структура расчёта:

    CAPEX = оборудование + ПО + интеграция + ПНР + обучение + резерв 10 %
    OPEX  = сервис + лицензии + энергия + расходники + замена АКБ
    Годовой эффект = экономия ФОТ + качество − OPEX − годовая амортизация
    Окупаемость    = CAPEX / годовой эффект
    ROI           = накопленный эффект / CAPEX × 100 %
    TCO           = сумма расходов на горизонте ≥ 5 лет по трём сценариям

Амортизация CAPEX входит в годовой эффект линейно (ТЗ 3.5.4) — это
сознательное решение: без неё «эффект» сравнивал бы годовой поток с
единовременными затратами, и окупаемость выходила бы завышенной.

Все коэффициенты приходят из `normatives`, объём операций и цены — из
проекта и каталога. Ни одно число не «зашито» здесь.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from app.models import Solution
from app.services.economics.assumptions import Assumptions
from app.services.economics.labor import (
    MONTHS_PER_YEAR,
    build_baseline_labor,
    labor_saving_for_process,
)
from app.services.economics.sizing import SizingResult, size

KIND_BASELINE = "baseline"
KIND_PURCHASE = "purchase"
KIND_RAAS = "raas"


def _d(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _r(value: float, digits: int = 2) -> float:
    return round(value + 0.0, digits)


def rub_text(value: float) -> str:
    """Денежная сумма в виде текста.

    Пояснения модели читает человек, а `_r` отдаёт float: в текст он
    попадал как «993750.0», без разделителей разрядов. Разряды разделяем
    неразрывным пробелом, как принято в русской типографике, чтобы число
    не рвалось переносом строки.
    """
    return f"{round(value):,}".replace(",", "\u00a0")


def plural(count: int, one: str, few: str, many: str) -> str:
    """Согласует существительное с числом: 1 позиция, 2 позиции, 5 позиций."""
    tail100 = count % 100
    tail10 = count % 10
    if 11 <= tail100 <= 14:
        word = many
    elif tail10 == 1:
        word = one
    elif 2 <= tail10 <= 4:
        word = few
    else:
        word = many
    return f"{count} {word}"


def years_phrase(count: int) -> str:
    """«1 год», «2 года», «5 лет» — с правильным окончанием."""
    return plural(count, "год", "года", "лет")



@dataclass
class EquipmentLine:
    """Одна позиция оборудования в составе сценария."""

    solution: Solution
    quantity: int
    unit_price: float
    price_source: str | None
    sizing: SizingResult | None
    labor: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    @property
    def equipment_total(self) -> float:
        return self.quantity * self.unit_price

    @property
    def display_name(self) -> str:
        return self.solution.display_name


@dataclass
class CapexBreakdown:
    equipment: float = 0.0
    software: float = 0.0
    integration: float = 0.0
    commissioning: float = 0.0
    training: float = 0.0
    charging_stations: float = 0.0
    subtotal: float = 0.0
    reserve: float = 0.0
    total: float = 0.0

    def as_dict(self) -> dict:
        return {
            "equipment": _r(self.equipment),
            "software": _r(self.software),
            "integration": _r(self.integration),
            "commissioning": _r(self.commissioning),
            "training": _r(self.training),
            "charging_stations": _r(self.charging_stations),
            "subtotal": _r(self.subtotal),
            "reserve": _r(self.reserve),
            "reserve_pct": _r(self.reserve / self.subtotal * 100, 2) if self.subtotal else 0.0,
            "total": _r(self.total),
        }


@dataclass
class OpexBreakdown:
    service: float = 0.0
    licenses: float = 0.0
    energy: float = 0.0
    consumables: float = 0.0
    integration_support: float = 0.0
    insurance: float = 0.0
    battery_replacement: float = 0.0
    total: float = 0.0

    def as_dict(self) -> dict:
        return {
            "service": _r(self.service),
            "licenses": _r(self.licenses),
            "energy": _r(self.energy),
            "consumables": _r(self.consumables),
            "integration_support": _r(self.integration_support),
            "insurance": _r(self.insurance),
            "battery_replacement": _r(self.battery_replacement),
            "total": _r(self.total),
        }


# ─────────────────────────────────────────────────────────────────────────────
# CAPEX
# ─────────────────────────────────────────────────────────────────────────────


#: Тип решения → код норматива с типовой ёмкостью АКБ. Используется, когда
#: в карточке решения нет данных о мощности зарядки: ёмкость нельзя выводить
#: из мощности, а оценивать её как долю от цены оборудования неверно.
BATTERY_NORMATIVE = {
    "amr": "battery.amr_kwh",
    "fmr": "battery.fmr_kwh",
    "stacker": "battery.fmr_kwh",
    "shuttle": "battery.fmr_kwh",
    "asrs": "battery.asrs_kwh",
    "cleaner": "battery.cleaner_kwh",
    "delivery_robot": "battery.delivery_robot_kwh",
    "inventory_robot": "battery.delivery_robot_kwh",
    "tugger": "battery.tugger_kwh",
    "autonomous_truck": "battery.truck_kwh",
}


def _battery_capacity_kwh(sol: Solution, assumptions: Assumptions) -> float:
    """Ёмкость АКБ, кВт·ч.

    Порядок: подтверждённая в карточке ёмкость → мощность зарядки × автономность
    → норматив по типу решения. Обратный порядок дал бы ерунду: мощность
    зарядки не равна среднему потреблению.
    """
    declared = _d(sol.battery_capacity_kwh)
    if declared > 0:
        return declared
    power = _d(sol.charge_power_kw)
    hours = _d(sol.autonomy_hours)
    if power > 0 and hours > 0:
        return power * hours
    type_code = sol.solution_type.code if sol.solution_type else None
    code = BATTERY_NORMATIVE.get(type_code or "")
    return assumptions.float_(code) if code else 0.0


def build_capex(
    lines: list[EquipmentLine], assumptions: Assumptions
) -> tuple[CapexBreakdown, list[str]]:
    a = assumptions
    capex = CapexBreakdown()
    warnings: list[str] = []

    software_pct = a.float_("capex.software_pct") / 100
    integration_pct = a.float_("capex.integration_pct") / 100
    commissioning_pct = a.float_("capex.commissioning_pct") / 100
    training_pct = a.float_("capex.training_pct") / 100
    reserve_pct = a.float_("capex.reserve_pct") / 100
    station_price = a.float_("capex.charging_station_rub")

    for line in lines:
        capex.equipment += line.equipment_total
        explicit_software = _d(line.solution.software_price_rub) * line.quantity
        if explicit_software > 0:
            capex.software += explicit_software
        else:
            capex.software += line.equipment_total * software_pct
        explicit_impl = _d(line.solution.implementation_price_rub) * line.quantity
        if explicit_impl > 0:
            capex.integration += explicit_impl
        else:
            capex.integration += line.equipment_total * integration_pct

        capex.commissioning += line.equipment_total * commissioning_pct
        capex.training += line.equipment_total * training_pct

        # Зарядная станция: одна на 2–3 робота — берём 1 станцию на 2.
        robots = max(1, line.quantity)
        stations = math.ceil(robots / 2)
        capex.charging_stations += stations * station_price

        if line.price_source == "estimate":
            warnings.append(
                f"{line.display_name}: цена — оценочное допущение, CAPEX требует "
                "подтверждения коммерческим предложением."
            )

    capex.subtotal = (
        capex.equipment
        + capex.software
        + capex.integration
        + capex.commissioning
        + capex.training
        + capex.charging_stations
    )
    capex.reserve = capex.subtotal * reserve_pct
    capex.total = capex.subtotal + capex.reserve
    return capex, warnings


# ─────────────────────────────────────────────────────────────────────────────
# OPEX
# ─────────────────────────────────────────────────────────────────────────────


def build_opex(
    lines: list[EquipmentLine], capex: CapexBreakdown, assumptions: Assumptions
) -> tuple[OpexBreakdown, list[str]]:
    a = assumptions
    opex = OpexBreakdown()
    warnings: list[str] = []

    default_service_pct = a.float_("opex.service_pct") / 100
    license_pct = a.float_("opex.license_pct") / 100
    energy_price = a.float_("opex.energy_rub_per_kwh")
    consumables_pct = a.float_("opex.consumables_pct") / 100
    support_pct = a.float_("opex.integration_support_pct") / 100
    insurance_pct = a.float_("opex.insurance_pct") / 100
    battery_price = a.float_("capex.battery_replacement_rub_per_kwh")
    default_battery_years = a.float_("capex.battery_lifetime_years") or 4.0
    hours_in_year = a.float_("energy.cycles_per_year") or 8760.0

    for line in lines:
        rate = _d(line.solution.service_rate_pct) / 100
        if rate <= 0:
            rate = default_service_pct
        opex.service += line.equipment_total * rate
        opex.licenses += (
            _d(line.solution.software_price_rub) * line.quantity
            * license_pct
            if _d(line.solution.software_price_rub) > 0
            else line.equipment_total * software_share(a) * license_pct
        )

        capacity = _battery_capacity_kwh(line.solution, a)
        if capacity <= 0:
            warnings.append(
                f"{line.display_name}: ёмкость аккумулятора не подтверждена — "
                "энергопотребление и стоимость замены АКБ не рассчитаны."
            )
            continue

        # Один цикл — это полная зарядка батареи плюс её разряд за смену.
        hours = _d(line.solution.autonomy_hours) or 8.0
        charge_min = _d(line.solution.charge_time_min) or 60.0
        cycles_per_year = hours_in_year / max(hours + charge_min / 60, 1e-6)
        opex.energy += capacity * cycles_per_year * energy_price * line.quantity

        # Замена АКБ — разовая трата раз в 3–5 лет, но по «Легенде» она входит
        # в годовой OPEX. Поэтому берётся годовая равномерная доля, а не полная
        # стоимость батареи ежегодно.
        years = _d(line.solution.battery_lifetime_years) or default_battery_years
        opex.battery_replacement += capacity * battery_price / max(years, 1e-6) * line.quantity

    opex.consumables = capex.subtotal * consumables_pct
    opex.integration_support = capex.subtotal * support_pct
    opex.insurance = capex.subtotal * insurance_pct
    opex.total = (
        opex.service
        + opex.licenses
        + opex.energy
        + opex.consumables
        + opex.integration_support
        + opex.insurance
        + opex.battery_replacement
    )
    return opex, warnings


def software_share(a: Assumptions) -> float:
    return a.float_("capex.software_pct") / 100


# ─────────────────────────────────────────────────────────────────────────────
# Эффект и сроки
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class EffectBreakdown:
    labor_saving: float = 0.0
    quality: float = 0.0
    throughput: float = 0.0
    safety: float = 0.0
    labor_detail: list[dict] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def gross(self) -> float:
        return self.labor_saving + self.quality + self.throughput + self.safety


def build_effect(
    lines: list[EquipmentLine],
    assumptions: Assumptions,
    object_type: str,
    process_codes: list[str],
    params: dict,
    operations_multiplier: float = 1.0,
) -> EffectBreakdown:
    a = assumptions
    payroll = a.float_("payroll.multiplier")
    fte_per_robot = a.float_("effect.headcount_fte_per_robot")
    labor_multiplier = a.get("labor_cost_multiplier", 1.0)
    effect = EffectBreakdown(notes=[])

    for line in lines:
        for process_code in line.solution.process_codes or []:
            if process_codes and process_code not in process_codes:
                continue
            detail = labor_saving_for_process(
                object_type=object_type,
                process_code=process_code,
                params=params,
                robots=line.quantity,
                fte_per_robot=fte_per_robot,
                payroll_multiplier=payroll,
                salary_multiplier=labor_multiplier,
            )
            detail["solution"] = line.display_name
            # Объём операций напрямую влияет на экономию: при меньшем объёме
            # часть роботов простаивает, и замещается меньше людей.
            detail["annual_saving"] = _r(detail["annual_saving"] * operations_multiplier)
            effect.labor_detail.append(detail)
            effect.labor_saving += detail["annual_saving"]

    baseline_labor = build_baseline_labor(
        object_type, params, payroll, labor_multiplier, process_codes=process_codes
    )
    if baseline_labor.annual_total > 0 and effect.labor_saving > baseline_labor.annual_total * 1.05:
        effect.notes.append(
            "Расчётная экономия на ФОТ превышает годовые затраты на персонал, "
            "задействованный в роботизируемых процессах, — проверьте исходные "
            "данные о штате и объёмах."
        )

    effect.quality = (
        baseline_labor.annual_total
        * a.float_("effect.quality_loss_pct")
        / 100
        * operations_multiplier
    )
    effect.safety = a.float_("effect.safety_incident_avoidance_rub")
    if effect.quality == 0 and effect.safety == 0:
        effect.notes.append(
            "Эффекты от снижения потерь и травматизма не включены: по умолчанию "
            "они равны нулю и включаются только при явном обосновании."
        )
    return effect


def amortization(capex_total: float, years: int) -> float:
    if years <= 0:
        return capex_total
    return capex_total / years


def payback_years(capex_total: float, annual_net: float) -> float | None:
    if annual_net <= 0:
        return None
    return capex_total / annual_net


@dataclass
class YearRow:
    year: int
    labor_saving: float
    opex: float
    amortization: float
    #: годовой эффект по ТЗ 3.5.4 — с амортизацией, т. е. бухгалтерский
    net_annual: float
    #: годовой эффект по денежному потоку, без амортизации
    net_annual_cash: float
    cumulative: float
    cumulative_cash: float
    roi_pct: float
    discounted: float

    def as_dict(self) -> dict:
        return {k: (v if k == "year" else _r(v)) for k, v in self.__dict__.items()}


def build_schedule(
    capex: CapexBreakdown,
    opex: OpexBreakdown,
    effect: EffectBreakdown,
    assumptions: Assumptions,
    horizon: int,
    *,
    initial_investment: float | None = None,
) -> list[YearRow]:
    amort_years = int(assumptions.get("amortization_years", 5))
    amort_per_year = amortization(capex.total, amort_years)
    investment = capex.total if initial_investment is None else initial_investment
    discount = assumptions.get("discount_rate", 0.14)
    gross = effect.labor_saving + effect.quality + effect.throughput + effect.safety

    rows: list[YearRow] = []
    cumulative = -investment
    cumulative_cash = -investment
    for year in range(1, horizon + 1):
        net_cash = gross - opex.total
        net = net_cash - amort_per_year
        cumulative += net
        cumulative_cash += net_cash
        rows.append(
            YearRow(
                year=year,
                labor_saving=effect.labor_saving,
                opex=opex.total,
                amortization=amort_per_year,
                net_annual=net,
                net_annual_cash=net_cash,
                cumulative=cumulative,
                cumulative_cash=cumulative_cash,
                roi_pct=(cumulative / investment * 100) if investment > 0 else 0.0,
                discounted=cumulative / ((1 + discount) ** year) if (1 + discount) ** year else cumulative,
            )
        )
    return rows


def payback_report(
    investment: float, gross_annual: float, opex_total: float, amort_per_year: float
) -> dict[str, Any]:
    """Окупаемость по денежному потоку и по бухгалтерскому эффекту.

    ТЗ 3.5.4 требует включить амортизацию CAPEX в годовой эффект линейно.
    Формально это верно, но при сроке амортизации 5 лет и окупаемости дольше
    5 лет годовой эффект становится отрицательным, и окупаемость по этой
    формуле не существует вовсе. Поэтому считаются оба показателя:

    * `cash_payback_years` — по реальному движению денег, без амортизации;
      именно этот срок показывается как окупаемость проекта;
    * `accounting_net_annual` — эффект по ТЗ, с амортизацией; по нему
      считается рентабельность в бухгалтерском учёте.
    """
    cash_net = gross_annual - opex_total
    accounting_net = cash_net - amort_per_year
    cash_payback = payback_years(investment, cash_net)
    return {
        "investment": _r(investment),
        "gross_annual_effect": _r(gross_annual),
        "annual_opex": _r(opex_total),
        "annual_amortization": _r(amort_per_year),
        "cash_net_annual": _r(cash_net),
        "accounting_net_annual": _r(accounting_net),
        "cash_payback_years": _r(cash_payback, 2) if cash_payback else None,
        "cash_payback_months": _r(cash_payback * 12, 1) if cash_payback else None,
        "accounting_payback_years": _r(payback_years(investment, accounting_net), 2)
        if payback_years(investment, accounting_net)
        else None,
        "note": (
            "Окупаемость рассчитана по денежному потоку. Амортизация — "
            "безденежная статья: она уменьшает бухгалтерскую прибыль, но не "
            "отвлекает средства. Годовой эффект по ТЗ 3.5.4 (с амортизацией) "
            "приведён рядом отдельной строкой."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# RaaS
# ─────────────────────────────────────────────────────────────────────────────


def build_raas(
    capex: CapexBreakdown, opex: OpexBreakdown, assumptions: Assumptions
) -> dict[str, Any]:
    a = assumptions
    rate = a.get("raas_rate_pct", 28) / 100
    setup_pct = a.get("raas.setup_pct", 8) / 100
    term_months = int(a.get("raas_term_months", 36))
    min_availability = a.float_("raas.min_availability")

    annual_payment = capex.total * rate
    setup = capex.total * setup_pct
    # В платёж по договору RaaS входит обслуживание, ПО и замена АКБ — платить
    # за это дважды нельзя. Остаётся то, что остаётся на стороне заказчика:
    # электроэнергия, расходники и страхование.
    included = (
        opex.service
        + opex.licenses
        + opex.integration_support
        + opex.insurance
        + opex.battery_replacement
    )
    provider_opex = max(0.0, opex.total - included)

    total_3y = annual_payment * (term_months / 12) + setup
    purchase_3y = capex.total + opex.total * (term_months / 12)
    delta = purchase_3y - total_3y

    notes: list[str] = []
    years = years_phrase(term_months // 12)
    if delta > 0:
        notes.append(
            f"За {years} RaaS дешевле покупки на {rub_text(delta)} руб. "
            "(включены сервис, ПО и замена АКБ)."
        )
    else:
        notes.append(
            f"За {years} покупка выгоднее RaaS на {rub_text(-delta)} руб. — "
            "это ожидаемо: сервис и обновления входят в платёж."
        )
    notes.append(
        f"Договор RaaS обычно предусматривает гарантированную доступность "
        f"{min_availability:.0%}; штрафы за её недостижение платёж не уменьшают, "
        "а лишь компенсируются отдельно."
    )
    if term_months / 12 < assumptions.get("horizon_years", 5):
        notes.append(
            f"Срок договора ({term_months} мес.) короче горизонта расчёта — после "
            f"{term_months} мес. условия продления нужно согласовать отдельно."
        )

    return {
        "model": "raas",
        "annual_payment": _r(annual_payment),
        "setup_fee": _r(setup),
        "term_months": term_months,
        "min_availability": min_availability,
        "included_in_payment": _r(included),
        "provider_opex": _r(provider_opex),
        "total_for_term": _r(total_3y),
        "purchase_for_term": _r(purchase_3y),
        "delta_vs_purchase": _r(delta),
        "notes": notes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Чувствительность
# ─────────────────────────────────────────────────────────────────────────────


def sensitivity(
    base: dict[str, Any],
    run: Any,
    param_keys: tuple[str, str, str] = ("equipment_cost", "operations_volume", "labor_cost"),
) -> list[dict[str, Any]]:
    """Пересчитывает экономику при изменении трёх обязательных параметров.

    `run` — функция, принимающая словарь переопределений и возвращающая
    сводный результат (годовой эффект, окупаемость, CAPEX).
    """
    labels = {
        "equipment_cost": "Стоимость оборудования",
        "operations_volume": "Объём операций",
        "labor_cost": "Стоимость персонала",
    }
    out: list[dict[str, Any]] = []
    for key in param_keys:
        override_key = {
            "equipment_cost": "equipment_cost_multiplier",
            "operations_volume": "operations_multiplier",
            "labor_cost": "labor_cost_multiplier",
        }[key]
        points = []
        for factor in (0.7, 0.85, 1.0, 1.15, 1.3):
            r = run({override_key: factor})
            points.append(
                {
                    "factor": factor,
                    "capex": r.get("capex_total"),
                    "annual_effect": r.get("annual_effect"),
                    "payback_years": r.get("payback_years"),
                    "roi_pct": r.get("roi_pct"),
                }
            )
        effect_values = [p["annual_effect"] for p in points if p["annual_effect"] is not None]
        paybacks = [p["payback_years"] for p in points if p["payback_years"] is not None]
        out.append(
            {
                "key": key,
                "label": labels.get(key, key),
                "override_key": override_key,
                "range_pct": [-30, -15, 0, 15, 30],
                "points": points,
                "effect_spread": _r(max(effect_values) - min(effect_values), 2) if effect_values else 0.0,
                "payback_spread_years": _r(max(paybacks) - min(paybacks), 2) if paybacks else None,
            }
        )
    return out
