"""Имитация работы роботов (ТЗ 3.6).

Бэкенд не «крутит» анимацию, а рассчитывает детерминированную раскладку, KPI
и расписание задач. Фронтенд только воспроизводит их. Так визуализация
подтверждает расчёт, а не украшает его: если числа на графике разошлись с
KPI, значит ошибка в расчёте, а не в анимации.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.deps import DbSession, LoggedIn, ensure_owner_or_admin
from app.core.errors import AppError
from app.models import Calculation, Project, Scenario, ScenarioSolution, Solution
from app.schemas.api import SimulationOut, SimulationRequest
from app.services.simulation.engine import scenario_robots, simulate_scenario

router = APIRouter(tags=["Имитация"])


def _load(db: DbSession, user, scenario_id: int) -> tuple[Scenario, Project]:
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


def _serialize(run: Any) -> dict[str, Any]:
    return {
        "id": run.id,
        "scenario_id": run.scenario_id,
        "status": run.status,
        "progress": run.progress,
        "speed_factor": float(run.speed_factor),
        "layout": run.layout,
        "kpi": run.kpi,
        "schedule": run.schedule,
        "error_message": run.error_message,
        "duration_ms": run.duration_ms,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


@router.post(
    "/scenarios/{scenario_id}/simulate",
    response_model=SimulationOut,
    status_code=status.HTTP_201_CREATED,
)
def simulate(
    scenario_id: int,
    payload: SimulationRequest,
    db: DbSession,
    user: LoggedIn,
    persist: bool = Query(default=True),
) -> dict[str, Any]:
    """Считает раскладку, KPI и расписание для сценария."""
    from app.models import SimulationRun

    scenario, project = _load(db, user, scenario_id)
    items = [
        (line.solution_id, int(line.quantity))
        for line in scenario.solutions
        if float(line.quantity) > 0
    ]
    if not items:
        raise AppError(
            "В сценарии нет оборудования для имитации.",
            code="empty_scenario",
            hint="Добавьте решения и рассчитайте сценарий.",
        )

    from app.core.config import settings
    from app.services.economics.assumptions import apply_overrides, load_assumptions

    assumptions = load_assumptions(db, settings.calc_model_version)
    apply_overrides(assumptions, scenario.assumptions or {})

    robots = scenario_robots(scenario)

    started = datetime.now(UTC)
    try:
        outcome = simulate_scenario(
            object_type=project.object_type.code,
            params=project.parameters or {},
            process_codes=list(project.process_codes or []),
            robots=robots,
            assumptions=assumptions,
            seed=payload.seed,
            include_schedule=payload.include_schedule,
        )
    except AppError:
        raise
    except Exception as exc:  # noqa: BLE001 — в ошибку имитации попадает всё
        raise AppError(
            f"Имитацию выполнить не удалось: {exc}",
            code="simulation_failed",
            hint="Проверьте, что параметры объекта заполнены и сценарий рассчитан.",
        ) from exc

    if not persist:
        return {
            "id": 0,
            "scenario_id": scenario.id,
            "status": "done",
            "progress": 100,
            "speed_factor": payload.speed_factor,
            "layout": outcome.layout,
            "kpi": outcome.kpi,
            "schedule": outcome.schedule,
            "error_message": None,
            "duration_ms": outcome.duration_ms,
            "created_at": started,
            "started_at": started,
            "finished_at": datetime.now(UTC),
        }

    from app.models import SimulationRun as _Run

    run = _Run(
        scenario_id=scenario.id,
        status="done",
        progress=100,
        speed_factor=payload.speed_factor,
        layout=outcome.layout,
        kpi=outcome.kpi,
        schedule=outcome.schedule,
        duration_ms=outcome.duration_ms,
        started_at=started,
        finished_at=datetime.now(UTC),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _serialize(run)


@router.get("/scenarios/{scenario_id}/simulations", response_model=list[SimulationOut])
def list_simulations(
    scenario_id: int, db: DbSession, user: LoggedIn, limit: int = Query(default=20, ge=1, le=100)
) -> list[dict[str, Any]]:
    from app.models import SimulationRun

    scenario, _ = _load(db, user, scenario_id)
    rows = db.scalars(
        select(SimulationRun)
        .where(SimulationRun.scenario_id == scenario.id)
        .order_by(SimulationRun.id.desc())
        .limit(limit)
    ).all()
    return [_serialize(r) for r in rows]


@router.get("/simulations/{run_id}", response_model=SimulationOut)
def get_simulation(run_id: int, db: DbSession, user: LoggedIn) -> dict[str, Any]:
    from app.models import SimulationRun

    run = db.get(SimulationRun, run_id)
    if run is None:
        raise AppError("Запуск имитации не найден.", code="not_found", status_code=404)
    _load(db, user, run.scenario_id)
    return _serialize(run)
