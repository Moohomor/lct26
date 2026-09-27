"""Экономические расчёты (ТЗ 3.5).

Расчёт всегда привязан к сценарию проекта: он хранит вход, а результат
сохраняется отдельной записью со снимком входа и версиями справочников.
Иначе через месяц нельзя понять, из каких цен и нормативов получена цифра,
которую пользователь видел на экране.
"""

from __future__ import annotations

import time
import uuid
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.deps import DbSession, LoggedIn, ensure_owner_or_admin
from app.core.errors import AppError
from app.models import Calculation, Project, Scenario, ScenarioSolution, Solution, SolutionType
from app.schemas.api import ScenarioItem
from app.services.economics.assumptions import (
    SCENARIO_OVERRIDABLE,
    describe,
    load_assumptions,
    override_limits,
    overrides_by_normative,
)
from app.services.economics.calculator import ScenarioInput, calculate

router = APIRouter(tags=["Экономические расчёты"])


def _load_scenario(db: DbSession, user, scenario_id: int) -> tuple[Scenario, Project]:
    scenario = db.scalar(
        select(Scenario)
        .where(Scenario.id == scenario_id)
        .options(
            selectinload(Scenario.project).selectinload(Project.object_type),
            selectinload(Scenario.solutions)
            .selectinload(ScenarioSolution.solution)
            .selectinload(Solution.solution_type),
        )
    )
    if scenario is None:
        raise AppError("Сценарий не найден.", code="not_found", status_code=404)
    ensure_owner_or_admin(user, scenario.project.user_id)
    return scenario, scenario.project


def _quantities(scenario: Scenario, *, auto: bool) -> dict[uuid.UUID, int | None]:
    """Количество по каждой позиции сценария.

    В режиме `auto` для незафиксированных позиций возвращается `None`:
    количество определит sizing внутри расчёта. Зафиксированное пользователем
    (`is_locked`) число не пересчитывается — если человек задал четыре робота
    осознанно, подбор не имеет права молча заменить это на три.
    """
    out: dict[uuid.UUID, int | None] = {}
    for line in scenario.solutions:
        if not auto or line.is_locked:
            out[line.solution_id] = int(line.quantity)
        else:
            out[line.solution_id] = None
    return out


@router.post("/scenarios/{scenario_id}/calculate")
def run_calculation(
    scenario_id: int,
    db: DbSession,
    user: LoggedIn,
    persist: bool = Query(default=True, description="Сохранить снимок расчёта"),
    with_sensitivity: bool = Query(default=True, description="Анализ чувствительности"),
    quantity_mode: str = Query(
        default="auto", pattern="^(auto|manual)$",
        description="auto — пересчитать по sizing, manual — взять из сценария",
    ),
) -> dict[str, Any]:
    scenario, project = _load_scenario(db, user, scenario_id)

    if scenario.kind == "baseline":
        items: list[tuple[uuid.UUID, int | None]] = []
    else:
        items = [(sid, q) for sid, q in _quantities(scenario, auto=quantity_mode == "auto").items()]

    if scenario.kind != "baseline" and not items:
        raise AppError(
            "В сценарии нет оборудования — считать нечего.",
            code="empty_scenario",
            hint="Добавьте решения через подбор или вручную.",
        )

    horizon = int(
        (scenario.assumptions or {}).get("horizon_years", scenario.horizon_years)
    )
    payload = ScenarioInput(
        object_type=project.object_type.code,
        object_type_name=project.object_type.name,
        process_codes=list(project.process_codes or []),
        params=dict(project.parameters or {}),
        items=items,
        assumptions_override=dict(scenario.assumptions or {}),
        horizon_years=horizon,
        kind=scenario.kind,
    )
    result = calculate(db, payload, with_sensitivity=with_sensitivity)

    if not persist:
        result["persisted"] = False
        return result

    # Ключевые цифры дублируются в колонки, чтобы список расчётов не
    # распаковывал JSONB для каждой строки.
    kind = scenario.kind
    source = result.get(kind) or result.get("purchase") or {}
    calc = Calculation(
        scenario_id=scenario.id,
        user_id=user.id,
        kind=kind,
        model_version=result["meta"]["model_version"],
        catalog_version=result["meta"].get("catalog_version"),
        params_version=project.params_version,
        capex_total=_dec(source.get("capex", {}).get("total")),
        annual_effect=_dec(source.get("effect", {}).get("net_annual_cash")),
        payback_years=_dec(source.get("payback_years")),
        input_snapshot={
            "object_type": project.object_type.code,
            "process_codes": payload.process_codes,
            "params": payload.params,
            "items": [[str(sid), q] for sid, q in payload.items],
            "assumptions_override": payload.assumptions_override,
            "horizon_years": horizon,
            "quantity_mode": quantity_mode,
        },
        result=result,
        duration_ms=result["meta"].get("duration_ms"),
    )
    db.add(calc)
    from datetime import UTC, datetime

    scenario.last_calculated_at = datetime.now(UTC)
    if project.status == "draft":
        project.status = "calculated"
    db.commit()
    db.refresh(calc)

    result["persisted"] = True
    result["calculation_id"] = calc.id
    return result


def _dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(round(float(value), 2)))
    except (TypeError, ValueError):
        return None


@router.get("/scenarios/{scenario_id}/calculate")
def preview_calculation(
    scenario_id: int,
    db: DbSession,
    user: LoggedIn,
    kind: str | None = Query(default=None, pattern="^(baseline|purchase|raas)$"),
    with_sensitivity: bool = Query(default=False),
) -> dict[str, Any]:
    """Предпросмотр без сохранения — для «посмотреть, как изменится расчёт»."""
    scenario, project = _load_scenario(db, user, scenario_id)
    items = [
        (line.solution_id, int(line.quantity))
        for line in scenario.solutions
        if float(line.quantity) > 0
    ] or [(line.solution_id, None) for line in scenario.solutions]
    payload = ScenarioInput(
        object_type=project.object_type.code,
        object_type_name=project.object_type.name,
        process_codes=list(project.process_codes or []),
        params=dict(project.parameters or {}),
        items=items,
        assumptions_override=dict(scenario.assumptions or {}),
        horizon_years=scenario.horizon_years,
        kind=kind or scenario.kind,
    )
    return calculate(db, payload, with_sensitivity=with_sensitivity)


@router.get("/scenarios/{scenario_id}/calculations/{calculation_id}")
def get_calculation(
    scenario_id: int, calculation_id: int, db: DbSession, user: LoggedIn
) -> dict[str, Any]:
    """Полный снимок расчёта: вход, результат и версии справочников."""
    scenario, project = _load_scenario(db, user, scenario_id)
    calc = db.scalar(
        select(Calculation).where(
            Calculation.id == calculation_id, Calculation.scenario_id == scenario.id
        )
    )
    if calc is None:
        raise AppError("Расчёт не найден.", code="not_found", status_code=404)
    return {
        "id": calc.id,
        "scenario_id": calc.scenario_id,
        "kind": calc.kind,
        "model_version": calc.model_version,
        "catalog_version": calc.catalog_version,
        "params_version": calc.params_version,
        "computed_at": calc.computed_at,
        "duration_ms": calc.duration_ms,
        "input": calc.input_snapshot,
        "result": calc.result,
    }


@router.get("/assumptions")
def list_assumptions(
    db: DbSession,
    model_version: str | None = Query(default=None),
    overridable_only: bool = Query(default=False, description="Только те, что может менять пользователь"),
) -> dict[str, Any]:
    """Действующие допущения расчёта.

    Открытый эндпоинт: пользователь должен видеть, из чего сложились цифры,
    иначе расчёт непроверяем (ТЗ 3.5.3).
    """
    version = model_version or settings.calc_model_version
    assumptions = load_assumptions(db, version)
    by_normative = overrides_by_normative()
    limits = override_limits()
    rows = describe(assumptions)
    for row in rows:
        codes = by_normative.get(row["code"], [])
        row["overridable_by_user"] = bool(codes)
        # Пользователь меняет не сам норматив, а множитель к нему, поэтому
        # интерфейсу нужен код переопределения, а не код норматива.
        row["override_codes"] = codes
        row["range"] = (
            [limits[codes[0]]["min"], limits[codes[0]]["max"]] if codes else None
        )
    if overridable_only:
        rows = [r for r in rows if r["overridable_by_user"]]
    return {
        "model_version": version,
        "count": len(rows),
        "assumptions": rows,
    }


@router.get("/assumptions/overridable")
def overridable_assumptions() -> dict[str, Any]:
    return {
        "count": len(SCENARIO_OVERRIDABLE),
        "assumptions": [
            {"code": code, **spec}
            for code, spec in sorted(override_limits().items())
        ],
        "note": (
            "Значения проверяются по указанным границам: за пределами диапазона "
            "расчёт невозможен, поэтому сервер отклоняет запрос, а не считает "
            "всё равно. Пустой normative означает, что допущение не опирается на "
            "норматив, а множит всю позицию целиком."
        ),
    }
