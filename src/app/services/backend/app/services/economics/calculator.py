"""Сценарный расчёт: три сценария ТЗ 3.5.5, чувствительность, сводка.

Это единственная точка, где экономика превращается в результат для API и
отчёта: sizing → состав оборудования → CAPEX/OPEX → эффект → окупаемость,
ROI, TCO → анализ чувствительности.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.models import CatalogVersion, Solution
from app.services.economics import engine as econ
from app.services.economics.assumptions import (
    Assumptions,
    apply_overrides,
    describe,
    load_assumptions,
)
from app.services.economics.labor import build_baseline_labor
from app.services.economics.sizing import size
from app.services.matching.requirements import build_requirements


@dataclass
class ScenarioInput:
    """Вход расчёта: что считаем."""

    object_type: str
    object_type_name: str
    process_codes: list[str]
    params: dict
    #: список позиций оборудования: (solution_id, количество)
    items: list[tuple[uuid.UUID, int]]
    assumptions_override: dict | None = None
    horizon_years: int = 5
    kind: str = econ.KIND_PURCHASE


def _catalog_version(db: Session) -> str | None:
    row = db.scalar(select(CatalogVersion).where(CatalogVersion.is_current.is_(True)))
    return row.version if row else None


def _load_solutions(db: Session, ids: list[uuid.UUID]) -> list[Solution]:
    if not ids:
        return []
    solutions = list(db.scalars(select(Solution).where(Solution.id.in_(ids))))
    found = {s.id for s in solutions}
    missing = [str(i) for i in ids if i not in found]
    if missing:
        raise AppError(
            "В расчёте указаны решения, которых нет в каталоге.",
            code="solution_not_found",
            hint="Обновите подборку: каталог мог измениться после импорта.",
            details={"missing": missing},
            status_code=409,
        )
    return solutions


def _resolve_price(sol: Solution, assumptions: Assumptions) -> tuple[float, str | None]:
    """Цена единицы и её источник. Если цены нет — нормативная оценка."""
    if sol.unit_price_rub is not None and _econ_num(sol.unit_price_rub) > 0:
        return _econ_num(sol.unit_price_rub), sol.price_source or "catalog"
    fallback = {
        "amr": "pricing.default_amr_rub",
        "fmr": "pricing.default_fmr_rub",
        "cleaner": "pricing.default_cleaner_rub",
        "tugger": "pricing.default_tugger_rub",
        "delivery_robot": "pricing.default_delivery_robot_rub",
        "asrs": "pricing.default_asrs_rub",
        "shuttle": "pricing.default_asrs_rub",
    }
    code = fallback.get(sol.solution_type.code if sol.solution_type else "", "pricing.default_other_rub")
    return assumptions.float_(code), "estimate"


def _econ_num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def auto_quantity(
    sol: Solution,
    assumptions: Assumptions,
    object_type: str,
    process_codes: list[str],
    params: dict,
) -> tuple[int, Any | None]:
    """Количество единиц по sizing и сам расчёт для показа пользователю.

    Считается максимум по процессам, к которым решение применимо: иначе
    робот окажется недозагруженным в пиковом процессе. Если производительность
    неизвестна, sizing невозможен — тогда возвращается 1 и `None`, а
    потребитель решает, что делать с такой позицией.
    """
    best: Any | None = None
    for process_code in sol.process_codes or []:
        if process_codes and process_code not in process_codes:
            continue
        _reqs, demand, _unit = build_requirements(object_type, process_code, params)
        if not demand or demand <= 0:
            continue
        thr = _econ_num(sol.throughput_per_hour)
        if thr <= 0:
            continue
        candidate = size(
            peak_demand=demand,
            unit_productivity=thr,
            load_factor=assumptions.float_("sizing.load_factor"),
            availability=assumptions.float_("sizing.availability"),
        )
        if best is None or candidate.units > best.units:
            best = candidate
    if best is None:
        return 1, None
    return max(1, int(best.units)), best


def _build_lines(
    solutions: list[Solution],
    quantities: dict[uuid.UUID, int | None],
    assumptions: Assumptions,
    object_type: str,
    process_codes: list[str],
    params: dict,
    equipment_cost_multiplier: float = 1.0,
) -> list[econ.EquipmentLine]:
    """Собирает позиции расчёта.

    `quantities[solution_id] = None` означает «количество не задано руками»:
    тогда его определяет sizing. Явное число пользователя не пересчитывается.
    """
    payroll = assumptions.float_("payroll.multiplier")
    fte_per_robot = assumptions.float_("effect.headcount_fte_per_robot")

    lines: list[econ.EquipmentLine] = []
    for sol in solutions:
        explicit = quantities.get(sol.id)
        sizing, sizing_result = auto_quantity(
            sol, assumptions, object_type, process_codes, params
        )
        if explicit is None:
            quantity = sizing
        else:
            quantity = max(1, int(explicit))

        price, price_source = _resolve_price(sol, assumptions)
        price *= equipment_cost_multiplier

        labor_detail: dict[str, Any] = {}
        for process_code in sol.process_codes or []:
            if process_codes and process_code not in process_codes:
                continue
            detail = econ.labor_saving_for_process(
                object_type=object_type,
                process_code=process_code,
                params=params,
                robots=quantity,
                fte_per_robot=fte_per_robot,
                payroll_multiplier=payroll,
            )
            if detail.get("annual_saving", 0) > labor_detail.get("annual_saving", 0):
                labor_detail = detail
            # Одна позиция не должна суммировать эффект по всем процессам:
            # выбираем процесс с максимальной экономией и считаем его один раз.

        line = econ.EquipmentLine(
            solution=sol,
            quantity=quantity,
            unit_price=price,
            price_source=price_source,
            sizing=sizing_result,
            labor=labor_detail,
        )
        if price_source == "estimate":
            line.warnings.append("Цена рассчитана по нормативной оценке, не по каталогу.")
        if explicit is not None and explicit != quantity:
            line.warnings.append(
                f"Количество задано вручную ({explicit}), расчёт по sizing дал {quantity}."
            )
        lines.append(line)
    return lines


def _scenario_result(
    *,
    kind: str,
    lines: list[econ.EquipmentLine],
    assumptions: Assumptions,
    object_type: str,
    process_codes: list[str],
    params: dict,
    horizon: int,
    operations_multiplier: float,
) -> dict[str, Any]:
    capex, capex_warnings = econ.build_capex(lines, assumptions)
    opex, opex_warnings = econ.build_opex(lines, capex, assumptions)
    effect = econ.build_effect(
        lines,
        assumptions,
        object_type,
        process_codes,
        params,
        operations_multiplier=operations_multiplier,
    )

    if kind == econ.KIND_RAAS:
        raas = econ.build_raas(capex, opex, assumptions)
        schedule = econ.build_schedule(
            capex,
            opex,
            effect,
            assumptions,
            horizon,
            initial_investment=raas["setup_fee"],
        )
        # В RaaS годовой платёж заменяет и OPEX, и амортизацию: заказчик не
        # владеет основными средствами и не амортизирует то, что ему не продано.
        payment = raas["annual_payment"] + raas["provider_opex"]
        cumulative = -raas["setup_fee"]
        for row in schedule:
            net_cash = effect.gross - payment
            cumulative += net_cash
            row.opex = round(payment, 2)
            row.amortization = 0.0
            row.net_annual = round(net_cash, 2)
            row.net_annual_cash = round(net_cash, 2)
            row.cumulative = round(cumulative, 2)
            row.cumulative_cash = round(cumulative, 2)
            row.roi_pct = (cumulative / raas["setup_fee"] * 100) if raas["setup_fee"] else 0.0
        investment = raas["setup_fee"]
    else:
        raas = None
        schedule = econ.build_schedule(capex, opex, effect, assumptions, horizon)
        investment = capex.total

    if kind == econ.KIND_RAAS:
        # В RaaS у заказчика нет основных средств, поэтому амортизация равна
        # нулю, а окупаемость — от вводного платежа.
        payment = raas["annual_payment"] + raas["provider_opex"]
        cash_net = effect.gross - payment
        payback_block = econ.payback_report(
            investment=investment,
            gross_annual=effect.gross,
            opex_total=payment,
            amort_per_year=0.0,
        )
    else:
        amort_years = int(assumptions.get("amortization_years", 5))
        amort_per_year = econ.amortization(capex.total, amort_years)
        payback_block = econ.payback_report(
            investment=investment,
            gross_annual=effect.gross,
            opex_total=opex.total,
            amort_per_year=amort_per_year,
        )

    net_annual = payback_block["accounting_net_annual"]
    payback = payback_block["cash_payback_years"]

    final_cumulative = schedule[-1].cumulative if schedule else 0.0
    roi = (final_cumulative / investment * 100) if investment > 0 else 0.0

    return {
        "kind": kind,
        "capex": capex.as_dict(),
        "opex": opex.as_dict(),
        "effect": {
            "labor_saving": round(effect.labor_saving, 2),
            "quality": round(effect.quality, 2),
            "throughput": round(effect.throughput, 2),
            "safety": round(effect.safety, 2),
            "gross_annual": round(effect.gross, 2),
            "net_annual": net_annual,
            "net_annual_cash": payback_block["cash_net_annual"],
            "labor_detail": effect.labor_detail,
            "notes": effect.notes,
        },
        "equipment": [
            {
                "solution_id": str(line.solution.id),
                "name": line.solution.name,
                "vendor": line.solution.vendor.name if line.solution.vendor else None,
                "quantity": line.quantity,
                "unit_price": round(line.unit_price, 2),
                "price_source": line.price_source,
                "equipment_total": round(line.equipment_total, 2),
                "sizing": line.sizing.as_dict() if line.sizing else None,
                "labor": line.labor,
                "warnings": line.warnings,
            }
            for line in lines
        ],
        "payback": payback_block,
        "payback_years": payback,
        "payback_months": payback_block["cash_payback_months"],
        "roi_pct": round(roi, 1),
        "schedule": [row.as_dict() for row in schedule],
        "raas": raas,
        "warnings": capex_warnings + opex_warnings,
        "investment": round(investment, 2),
    }


def calculate(
    db: Session, payload: ScenarioInput, *, with_sensitivity: bool = True
) -> dict[str, Any]:
    """Полный расчёт по трём сценариям плюс анализ чувствительности."""
    started = time.perf_counter()

    assumptions = load_assumptions(db, settings.calc_model_version)
    apply_overrides(assumptions, payload.assumptions_override)
    horizon = int(
        (payload.assumptions_override or {}).get("horizon_years", payload.horizon_years)
        or assumptions.get("calc.horizon_years", 5)
    )
    # Горизонт расчёта не может быть короче минимального по ТЗ.
    horizon = max(int(assumptions.get("calc.horizon_years", 5)), horizon)

    ids = [uid for uid, _q in payload.items]
    solutions = _load_solutions(db, ids)
    quantities = {uid: q for uid, q in payload.items}

    def run_kind(kind: str, overrides: dict | None = None) -> dict[str, Any]:
        local = load_assumptions(db, settings.calc_model_version)
        apply_overrides(local, overrides or payload.assumptions_override)
        lines = _build_lines(
            solutions,
            quantities,
            local,
            payload.object_type,
            payload.process_codes,
            payload.params,
            equipment_cost_multiplier=local.get("equipment_cost_multiplier", 1.0),
        )
        return _scenario_result(
            kind=kind,
            lines=lines,
            assumptions=local,
            object_type=payload.object_type,
            process_codes=payload.process_codes,
            params=payload.params,
            horizon=horizon,
            operations_multiplier=local.get("operations_multiplier", 1.0),
        )

    # Сценарий «до роботизации» — сравнительная база без CAPEX. Считается по
    # персоналу именно тех процессов, которые автоматизируются: сравнивать
    # расходы на роботизацию со всем штатом объекта было бы сравнением разных
    # по величине величин.
    baseline_labor = build_baseline_labor(
        payload.object_type,
        payload.params,
        assumptions.float_("payroll.multiplier"),
        process_codes=payload.process_codes,
    )
    baseline_notes = [
        "Сценарий «до роботизации»: текущие годовые затраты на персонал, "
        "выполняющий роботизируемые процессы.",
    ]
    if baseline_labor.missing_headcount:
        baseline_notes.append(
            "Численность персонала не указана в датасете для: "
            + ", ".join(baseline_labor.missing_headcount)
            + ". База сравнения занижена — уточните исходные данные."
        )
    if not payload.process_codes:
        baseline_notes.append(
            "Процессы не выбраны: в базу сравнения включён весь персонал объекта."
        )
    baseline = {
        "kind": econ.KIND_BASELINE,
        "annual_cost": round(baseline_labor.annual_total, 2),
        "labor": baseline_labor.as_dict(),
        "capex": econ.CapexBreakdown().as_dict(),
        "opex": econ.OpexBreakdown().as_dict(),
        "effect": {
            "gross_annual": 0.0,
            "net_annual": 0.0,
            "notes": baseline_notes,
        },
        "equipment": [],
        "payback_years": None,
        "roi_pct": 0.0,
        "schedule": [],
        "warnings": baseline_notes if baseline_labor.missing_headcount else [],
        "investment": 0.0,
    }

    purchase = run_kind(econ.KIND_PURCHASE)
    raas = run_kind(econ.KIND_RAAS)

    # Персонал, который роботизация не замещает: объект продолжает работать,
    # поэтому эти расходы остаются в обоих сценариях с оборудованием.
    residual_labor = max(
        0.0,
        baseline_labor.annual_total - purchase["effect"]["labor_saving"],
    )
    for scenario in (purchase, raas):
        scenario["residual_labor_annual"] = round(residual_labor, 2)

    # TCO на горизонте расчёта по всем трём сценариям.
    tco = _build_tco(baseline, purchase, raas, horizon, residual_labor)

    sens: list[dict[str, Any]] = []
    if with_sensitivity and payload.items:
        def sensitivity_run(overrides: dict) -> dict[str, Any]:
            r = run_kind(econ.KIND_PURCHASE, overrides)
            return {
                "capex_total": r["capex"]["total"],
                # Денежный эффект: он согласован с окупаемостью, иначе
                # график чувствительности показывал бы отрицательные
                # величины там, где проект окупается.
                "annual_effect": r["effect"]["net_annual_cash"],
                "payback_years": r["payback_years"],
                "roi_pct": r["roi_pct"],
            }

        sens = econ.sensitivity(purchase, sensitivity_run)

    warnings = purchase["warnings"] + raas["warnings"]
    warnings.append(
        f"Расчёт по {len(payload.items)} позициям оборудования на горизонте {horizon} лет."
    )
    if residual_labor > 0:
        warnings.append(
            f"Роботизация замещает не весь персонал: остаточные расходы на ФОТ "
            f"{residual_labor:,.0f} руб/год учтены в сценариях покупки и RaaS.".replace(",", " ")
        )

    return {
        "meta": {
            "model_version": settings.calc_model_version,
            "catalog_version": _catalog_version(db),
            "horizon_years": horizon,
            "object_type": payload.object_type,
            "object_type_name": payload.object_type_name,
            "process_codes": payload.process_codes,
            "computed_at": datetime.now(UTC).isoformat(),
            "duration_ms": int((time.perf_counter() - started) * 1000),
        },
        "baseline": baseline,
        "purchase": purchase,
        "raas": raas,
        "tco": tco,
        "sensitivity": sens,
        "assumptions": describe(assumptions),
        "warnings": warnings,
    }


def _build_tco(
    baseline: dict,
    purchase: dict,
    raas: dict,
    horizon: int,
    residual_labor: float,
) -> dict[str, Any]:
    """Совокупная стоимость владения за горизонт по трём сценариям.

    Ключевой момент: в сценариях покупки и RaaS учитывается остаточный ФОТ.
    Роботы замещают часть сотрудников, но объект продолжает работать и человек
    нужен. Сравнивать «CAPEX + OPEX» с «полной ФОТ объекта» — сравнение разных
    по величине сумм, из которого автоматически получается красивый и неверный
    вывод о выгоде.
    """
    def tco_of(scenario: dict) -> dict[str, Any]:
        if scenario["kind"] == econ.KIND_BASELINE:
            annual = scenario["annual_cost"]
            return {
                "kind": scenario["kind"],
                "total": round(annual * horizon, 2),
                "annual": round(annual, 2),
                "setup": 0.0,
                "residual_labor_annual": 0.0,
                "breakdown": {
                    "персонал за год": round(annual, 2),
                    "единовременные затраты": 0.0,
                },
            }

        capex_total = scenario["capex"]["total"]
        if scenario["kind"] == econ.KIND_RAAS:
            raas_info = scenario["raas"]
            robot_cost = raas_info["annual_payment"] + raas_info["provider_opex"]
            setup = raas_info["setup_fee"]
        else:
            robot_cost = scenario["opex"]["total"]
            setup = capex_total

        annual = robot_cost + residual_labor
        return {
            "kind": scenario["kind"],
            "total": round(setup + annual * horizon, 2),
            "annual": round(annual, 2),
            "setup": round(setup, 2),
            "residual_labor_annual": round(residual_labor, 2),
            "breakdown": {
                "единовременные затраты": round(setup, 2),
                "обслуживание техники за год": round(robot_cost, 2),
                "остаточный ФОТ за год": round(residual_labor, 2),
                "в том числе замена АКБ": round(
                    scenario["opex"]["battery_replacement"], 2
                ),
            },
        }

    base_tco = tco_of(baseline)
    purchase_tco = tco_of(purchase)
    raas_tco = tco_of(raas)

    best = min(
        (("baseline", base_tco), ("purchase", purchase_tco), ("raas", raas_tco)),
        key=lambda pair: pair[1]["total"],
    )
    # Экономия — положительное число, если вариант дешевле покупки.
    saving = {
        "baseline": round(purchase_tco["total"] - base_tco["total"], 2),
        "raas": round(purchase_tco["total"] - raas_tco["total"], 2),
    }
    return {
        "horizon_years": horizon,
        "scenarios": {
            "baseline": base_tco,
            "purchase": purchase_tco,
            "raas": raas_tco,
        },
        "best_option": best[0],
        "saving_vs_purchase": saving,
        "note": (
            "Стоимость владения за "
            f"{horizon} лет. Во всех сценариях учтён остаточный ФОТ: "
            "автоматизация замещает часть сотрудников, но не весь штат."
        ),
    }
