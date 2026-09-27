"""Проекты пользователя: параметры объекта, подбор решений, сценарии (ТЗ 3.1, 3.4).

Все эндпоинты проверяют владельца: проект одного пользователя не должен быть
виден другому, кроме администратора. Проверка вынесена в `ensure_owner_or_admin`,
чтобы правило звучало одинаково везде.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.v1.routes.reference import SOLUTION_LIST_LOAD, serialize_solution
from app.core.deps import DbSession, LoggedIn, ensure_owner_or_admin
from app.core.errors import AppError
from app.models import (
    Calculation,
    ObjectType,
    Parameter,
    Project,
    ProjectSolution,
    Scenario,
    ScenarioSolution,
    Solution,
)
from app.schemas.api import (
    ProjectCreate,
    ProjectDetail,
    ProjectOut,
    ProjectSolutionCreate,
    ProjectSolutionOut,
    ProjectUpdate,
    ScenarioCreate,
    ScenarioOut,
    ScenarioSolutionOut,
    ScenarioUpdate,
)

router = APIRouter(prefix="/projects", tags=["Проекты"])


# ── Вспомогательное ────────────────────────────────────────────────────────


def _object_type_by_code(db: DbSession, code: str) -> ObjectType:
    ot = db.scalar(select(ObjectType).where(ObjectType.code == code))
    if ot is None:
        raise AppError(
            f"Тип объекта «{code}» неизвестен.",
            code="not_found",
            hint="Допустимые коды: warehouse, airport, medical.",
            status_code=404,
        )
    return ot


def _validate_parameters(db: DbSession, object_type_id: int, values: dict[str, Any]) -> dict[str, Any]:
    """Проверяет коды и значения параметров объекта.

    Неизвестный код — ошибка, а не «молча игнорируем»: иначе опечатка в
    интерфейсе тихо исключает параметр из расчёта, и результат выглядит
    корректным, хотя посчитан не по тому.
    """
    if not values:
        return {}
    known = {
        p.code: p
        for p in db.scalars(
            select(Parameter).where(Parameter.object_type_id == object_type_id)
        )
    }
    unknown = sorted(set(values) - set(known))
    if unknown:
        raise AppError(
            f"Неизвестные параметры: {', '.join(unknown)}.",
            code="unknown_parameters",
            hint="Список допустимых кодов — GET /api/v1/object-types/{code}/parameters.",
        )
    out: dict[str, Any] = {}
    problems: list[str] = []
    for code, value in values.items():
        param = known[code]
        if value is None:
            continue
        out[code] = _coerce(param, value, problems)
    if problems:
        raise AppError(
            "Часть параметров вне допустимого диапазона.",
            code="invalid_parameters",
            details={"problems": problems},
            hint="Значения по умолчанию — GET /api/v1/object-types/{code}/parameters/defaults.",
        )
    return out


def _option_values(options: list[Any]) -> set[str]:
    """Допустимые значения перечисления в виде строк.

    Импорт из книги организатора кладёт простой список строк, но администратор
    через API может задать вариант с подписью: `{"value": "drive_in",
    "label": "Drive-in"}`. Форма проверки должна понимать оба вида, иначе
    перечисление, заведённое через админку, отвергало бы собственные же
    значения.
    """
    out: set[str] = set()
    for option in options or ():
        if isinstance(option, dict):
            raw = option.get("value", option.get("label"))
            if raw is not None:
                out.add(str(raw))
        else:
            out.add(str(option))
    return out


def _coerce(param: Parameter, value: Any, problems: list[str]) -> Any:
    """Приводит значение к типу параметра и проверяет границы."""
    kind = param.value_type
    label = f"{param.name} ({param.code})"
    try:
        if kind in ("number", "percent"):
            value = float(str(value).replace(",", "."))
        elif kind == "integer":
            value = int(float(str(value).replace(",", ".")))
        elif kind == "bool":
            if isinstance(value, bool):
                pass
            else:
                text = str(value).strip().lower()
                if text in ("1", "true", "да", "yes", "y"):
                    value = True
                elif text in ("0", "false", "нет", "no", "n"):
                    value = False
                else:
                    raise ValueError(value)
        elif kind == "text":
            value = str(value)[:2000]
    except (TypeError, ValueError):
        problems.append(f"{label}: значение «{value}» не является {kind}")
        return value

    if param.options and kind == "enum":
        allowed = _option_values(param.options)
        if str(value) not in allowed:
            problems.append(
                f"{label}: допустимые значения — {', '.join(sorted(allowed))}"
            )
    if kind in ("number", "percent", "integer"):
        if param.min_value is not None and value < float(param.min_value):
            problems.append(f"{label}: минимум {float(param.min_value)}, задано {value}")
        if param.max_value is not None and value > float(param.max_value):
            problems.append(f"{label}: максимум {float(param.max_value)}, задано {value}")
    return value


def _params_version(db: DbSession, object_type_id: int) -> str:
    """Отпечаток справочника параметров: меняется при правке администратором."""
    last = db.scalar(
        select(func.max(Parameter.updated_at)).where(Parameter.object_type_id == object_type_id)
    )
    count = db.scalar(
        select(func.count()).select_from(Parameter).where(Parameter.object_type_id == object_type_id)
    ) or 0
    return f"{count}-{(last.timestamp() if last else 0):.0f}"


def _project_out(p: Project) -> dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "object_type": p.object_type.code if p.object_type else "",
        "object_type_name": p.object_type.name if p.object_type else None,
        "status": p.status,
        "organization": p.organization,
        "description": p.description,
        "parameters": p.parameters or {},
        "process_codes": p.process_codes or [],
        "user_id": p.user_id,
        "is_demo": p.is_demo,
        "created_at": p.created_at,
        "updated_at": p.updated_at,
    }


def _completion(p: Project) -> dict[str, Any]:
    """Насколько проект готов к расчёту — чтобы форма подсказывала, что заполнить."""
    values = p.parameters or {}
    filled = sum(1 for v in values.values() if v not in (None, ""))
    return {
        "parameters_filled": filled,
        "parameters_total": len(values),
        "parameters_missing": sorted(
            code for code, v in values.items() if v in (None, "")
        ),
        "processes_selected": len(p.process_codes or []),
        "scenarios": len(p.scenarios),
        "solutions": len(p.solutions),
        "is_ready_for_matching": bool(p.process_codes),
        "is_ready_for_calculation": bool(p.process_codes) and filled > 0,
    }


def _load_project(db: DbSession, user, project_id: uuid.UUID) -> Project:
    project = db.scalar(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.object_type),
            selectinload(Project.scenarios).selectinload(Scenario.solutions),
            selectinload(Project.scenarios).selectinload(Scenario.calculations),
            selectinload(Project.solutions)
            .selectinload(ProjectSolution.solution)
            .options(*SOLUTION_LIST_LOAD),
        )
    )
    if project is None:
        raise AppError(
            "Проект не найден.",
            code="not_found",
            status_code=404,
        )
    ensure_owner_or_admin(user, project.user_id)
    return project


def _scenario_out(s: Scenario) -> dict[str, Any]:
    return {
        "id": s.id,
        "project_id": s.project_id,
        "name": s.name,
        "kind": s.kind,
        "description": s.description,
        "assumptions": s.assumptions or {},
        "horizon_years": s.horizon_years,
        "order_index": s.order_index,
        "created_at": s.created_at,
        "last_calculated_at": s.last_calculated_at,
        "items": [
            {
                "id": line.id,
                "scenario_id": line.scenario_id,
                "solution_id": line.solution_id,
                "solution_name": line.solution.name if line.solution else "",
                "solution_type": line.solution.solution_type.code
                if line.solution and line.solution.solution_type
                else None,
                "quantity": float(line.quantity),
                "is_locked": line.is_locked,
                "note": line.note,
            }
            for line in s.solutions
        ],
        "latest_calculation_id": s.calculations[0].id if s.calculations else None,
    }


# ── Проекты ────────────────────────────────────────────────────────────────


@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: DbSession,
    user: LoggedIn,
    status_filter: str | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, max_length=200),
    include_demo: bool = Query(default=True, description="Показывать демонстрационные проекты"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[dict[str, Any]]:
    stmt = select(Project).join(ObjectType).options(selectinload(Project.object_type))
    if not user.is_admin:
        stmt = stmt.where(Project.user_id == user.id)
    if status_filter:
        stmt = stmt.where(Project.status == status_filter)
    if not include_demo:
        stmt = stmt.where(Project.is_demo.is_(False))
    if search:
        stmt = stmt.where(Project.name.ilike(f"%{search.strip()}%"))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(
        stmt.order_by(Project.updated_at.desc()).limit(limit).offset(offset)
    ).all()
    return [_project_out(p) for p in rows]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: DbSession, user: LoggedIn) -> dict[str, Any]:
    ot = _object_type_by_code(db, payload.object_type)
    params = _validate_parameters(db, ot.id, payload.parameters)
    process_codes = _validate_processes(db, ot.id, payload.process_codes)

    project = Project(
        user_id=user.id,
        object_type_id=ot.id,
        name=payload.name.strip(),
        description=payload.description,
        organization=payload.organization or user.organization,
        parameters=params,
        process_codes=process_codes,
        params_version=_params_version(db, ot.id),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_out(project)


def _validate_processes(db: DbSession, object_type_id: int, codes: list[str]) -> list[str]:
    """Оставляет только процессы, существующие у этого типа объекта."""
    from app.models import Process

    if not codes:
        return []
    known = {
        c
        for (c,) in db.execute(
            select(Process.code).where(Process.object_type_id == object_type_id)
        )
    }
    unknown = sorted(set(codes) - known)
    if unknown:
        raise AppError(
            f"Процессы не относятся к этому типу объекта: {', '.join(unknown)}.",
            code="unknown_processes",
            hint="Список — GET /api/v1/object-types/{code}.",
        )
    return list(dict.fromkeys(codes))


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project(project_id: uuid.UUID, db: DbSession, user: LoggedIn) -> dict[str, Any]:
    project = _load_project(db, user, project_id)
    return {
        **_project_out(project),
        "completion": _completion(project),
        "scenarios": [_scenario_out(s) for s in project.scenarios],
        "latest_calculations": [
            _calc_out(c)
            for s in project.scenarios
            for c in s.calculations[:1]
        ],
    }


def _calc_out(c: Calculation) -> dict[str, Any]:
    return {
        "id": c.id,
        "scenario_id": c.scenario_id,
        "kind": c.kind,
        "model_version": c.model_version,
        "catalog_version": c.catalog_version,
        "params_version": c.params_version,
        "payback_years": float(c.payback_years) if c.payback_years is not None else None,
        "annual_effect": float(c.annual_effect) if c.annual_effect is not None else None,
        "capex_total": float(c.capex_total) if c.capex_total is not None else None,
        "duration_ms": c.duration_ms,
        "computed_at": c.computed_at,
        "user_id": c.user_id,
    }


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID, payload: ProjectUpdate, db: DbSession, user: LoggedIn
) -> dict[str, Any]:
    project = _load_project(db, user, project_id)
    if payload.name is not None:
        project.name = payload.name.strip() or project.name
    if payload.organization is not None:
        project.organization = payload.organization
    if payload.description is not None:
        project.description = payload.description
    if payload.parameters is not None:
        merged = {**(project.parameters or {}), **payload.parameters}
        project.parameters = _validate_parameters(db, project.object_type_id, merged)
        project.params_version = _params_version(db, project.object_type_id)
    if payload.process_codes is not None:
        project.process_codes = _validate_processes(
            db, project.object_type_id, payload.process_codes
        )
    db.commit()
    db.refresh(project)
    return _project_out(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, db: DbSession, user: LoggedIn) -> None:
    project = _load_project(db, user, project_id)
    db.delete(project)
    db.commit()


@router.post("/{project_id}/duplicate", response_model=ProjectOut, status_code=201)
def duplicate_project(project_id: uuid.UUID, db: DbSession, user: LoggedIn) -> dict[str, Any]:
    """Копия проекта под новым именем — чтобы сравнить два варианта расчёта."""
    source = _load_project(db, user, project_id)
    copy = Project(
        user_id=user.id,
        object_type_id=source.object_type_id,
        name=f"{source.name} — копия",
        description=source.description,
        organization=source.organization,
        parameters=dict(source.parameters or {}),
        process_codes=list(source.process_codes or []),
        params_version=source.params_version,
    )
    db.add(copy)
    db.flush()
    for ps in source.solutions:
        db.add(
            ProjectSolution(
                project_id=copy.id,
                solution_id=ps.solution_id,
                added_manually=ps.added_manually,
                warning=ps.warning,
                match_score=ps.match_score,
                match_reasons=ps.match_reasons,
            )
        )
    db.commit()
    db.refresh(copy)
    return _project_out(copy)


# ── Решения в подборке проекта ─────────────────────────────────────────────


def _ps_out(ps: ProjectSolution) -> dict[str, Any]:
    s = ps.solution
    return {
        "id": ps.id,
        "project_id": ps.project_id,
        "solution_id": ps.solution_id,
        "added_manually": ps.added_manually,
        "warning": ps.warning,
        "match_score": float(ps.match_score) if ps.match_score is not None else None,
        "match_reasons": ps.match_reasons,
        "solution": serialize_solution(s) if s else None,
    }


@router.get("/{project_id}/solutions", response_model=list[ProjectSolutionOut])
def list_project_solutions(
    project_id: uuid.UUID, db: DbSession, user: LoggedIn
) -> list[dict[str, Any]]:
    project = _load_project(db, user, project_id)
    return [_ps_out(ps) for ps in project.solutions]


@router.post(
    "/{project_id}/solutions",
    response_model=ProjectSolutionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_project_solution(
    project_id: uuid.UUID, payload: ProjectSolutionCreate, db: DbSession, user: LoggedIn
) -> dict[str, Any]:
    project = _load_project(db, user, project_id)
    if db.get(Solution, payload.solution_id) is None:
        raise AppError("Решение не найдено в каталоге.", code="not_found", status_code=404)
    exists = db.scalar(
        select(ProjectSolution.id).where(
            ProjectSolution.project_id == project.id,
            ProjectSolution.solution_id == payload.solution_id,
        )
    )
    if exists is not None:
        raise AppError(
            "Решение уже добавлено в проект.",
            code="duplicate",
            hint="Измените количество в сценарии.",
            status_code=409,
        )
    link = ProjectSolution(
        project_id=project.id,
        solution_id=payload.solution_id,
        added_manually=payload.added_manually,
        warning=payload.warning,
        match_score=payload.match_score,
        match_reasons=payload.match_reasons,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return _ps_out(link)


@router.delete("/{project_id}/solutions/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_solution(
    project_id: uuid.UUID, link_id: uuid.UUID, db: DbSession, user: LoggedIn
) -> None:
    project = _load_project(db, user, project_id)
    link = db.get(ProjectSolution, link_id)
    if link is None or link.project_id != project.id:
        raise AppError("Решение не найдено в проекте.", code="not_found", status_code=404)
    db.delete(link)
    db.commit()


# ── Сценарии ───────────────────────────────────────────────────────────────


@router.get("/{project_id}/scenarios", response_model=list[ScenarioOut])
def list_scenarios(project_id: uuid.UUID, db: DbSession, user: LoggedIn) -> list[dict[str, Any]]:
    project = _load_project(db, user, project_id)
    return [_scenario_out(s) for s in project.scenarios]


@router.post(
    "/{project_id}/scenarios", response_model=ScenarioOut, status_code=status.HTTP_201_CREATED
)
def create_scenario(
    project_id: uuid.UUID, payload: ScenarioCreate, db: DbSession, user: LoggedIn
) -> dict[str, Any]:
    from app.services.economics.assumptions import SCENARIO_OVERRIDABLE

    project = _load_project(db, user, project_id)
    unknown = sorted(set(payload.assumptions) - set(SCENARIO_OVERRIDABLE))
    if unknown:
        raise AppError(
            f"Допущения с такими кодами не предусмотрены: {', '.join(unknown)}.",
            code="unknown_assumptions",
            hint=f"Переопределяемые: {', '.join(sorted(SCENARIO_OVERRIDABLE))}.",
        )

    scenario = Scenario(
        project_id=project.id,
        name=payload.name.strip(),
        kind=payload.kind,
        description=payload.description,
        assumptions=payload.assumptions,
        horizon_years=payload.horizon_years,
        order_index=len(project.scenarios),
    )
    db.add(scenario)
    db.flush()
    for item in payload.items:
        if db.get(Solution, item.solution_id) is None:
            raise AppError(
                f"Решение {item.solution_id} не найдено в каталоге.",
                code="not_found",
                status_code=404,
            )
        db.add(
            ScenarioSolution(
                scenario_id=scenario.id,
                solution_id=item.solution_id,
                quantity=item.quantity,
            )
        )
    db.commit()
    db.refresh(scenario)
    return _scenario_out(scenario)


@router.get("/{project_id}/scenarios/{scenario_id}", response_model=ScenarioOut)
def get_scenario(
    project_id: uuid.UUID, scenario_id: int, db: DbSession, user: LoggedIn
) -> dict[str, Any]:
    project = _load_project(db, user, project_id)
    scenario = db.scalar(
        select(Scenario)
        .where(Scenario.id == scenario_id, Scenario.project_id == project.id)
        .options(
            selectinload(Scenario.solutions)
            .selectinload(ScenarioSolution.solution)
            .options(*SOLUTION_LIST_LOAD),
            selectinload(Scenario.calculations),
        )
    )
    if scenario is None:
        raise AppError("Сценарий не найден.", code="not_found", status_code=404)
    return _scenario_out(scenario)


@router.patch("/{project_id}/scenarios/{scenario_id}", response_model=ScenarioOut)
def update_scenario(
    project_id: uuid.UUID,
    scenario_id: int,
    payload: ScenarioUpdate,
    db: DbSession,
    user: LoggedIn,
) -> dict[str, Any]:
    from app.services.economics.assumptions import SCENARIO_OVERRIDABLE

    project = _load_project(db, user, project_id)
    scenario = db.scalar(
        select(Scenario)
        .where(Scenario.id == scenario_id, Scenario.project_id == project.id)
        .options(
            selectinload(Scenario.solutions)
            .selectinload(ScenarioSolution.solution)
            .options(*SOLUTION_LIST_LOAD),
            selectinload(Scenario.calculations),
        )
    )
    if scenario is None:
        raise AppError("Сценарий не найден.", code="not_found", status_code=404)

    if payload.name is not None:
        scenario.name = payload.name.strip() or scenario.name
    if payload.description is not None:
        scenario.description = payload.description
    if payload.horizon_years is not None:
        scenario.horizon_years = payload.horizon_years
    if payload.assumptions is not None:
        unknown = sorted(set(payload.assumptions) - set(SCENARIO_OVERRIDABLE))
        if unknown:
            raise AppError(
                f"Допущения с такими кодами не предусмотрены: {', '.join(unknown)}.",
                code="unknown_assumptions",
                hint=f"Переопределяемые: {', '.join(sorted(SCENARIO_OVERRIDABLE))}.",
            )
        scenario.assumptions = payload.assumptions

    if payload.items is not None:
        wanted = {i.solution_id: i.quantity for i in payload.items}
        for line in scenario.solutions:
            if line.solution_id not in wanted:
                db.delete(line)
        for solution_id, qty in wanted.items():
            if db.get(Solution, solution_id) is None:
                raise AppError(
                    f"Решение {solution_id} не найдено в каталоге.",
                    code="not_found",
                    status_code=404,
                )
            line = next((l for l in scenario.solutions if l.solution_id == solution_id), None)
            if line is None:
                db.add(ScenarioSolution(scenario_id=scenario.id, solution_id=solution_id, quantity=qty))
            else:
                line.quantity = qty
    db.commit()
    db.refresh(scenario)
    return _scenario_out(scenario)


@router.delete("/{project_id}/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    project_id: uuid.UUID, scenario_id: int, db: DbSession, user: LoggedIn
) -> None:
    project = _load_project(db, user, project_id)
    scenario = db.scalar(
        select(Scenario).where(Scenario.id == scenario_id, Scenario.project_id == project.id)
    )
    if scenario is None:
        raise AppError("Сценарий не найден.", code="not_found", status_code=404)
    db.delete(scenario)
    db.commit()


@router.get("/{project_id}/scenarios/{scenario_id}/calculations")
def list_calculations(
    project_id: uuid.UUID, scenario_id: int, db: DbSession, user: LoggedIn
) -> list[dict[str, Any]]:
    project = _load_project(db, user, project_id)
    rows = db.scalars(
        select(Calculation)
        .join(Scenario, Scenario.id == Calculation.scenario_id)
        .where(Scenario.project_id == project.id, Calculation.scenario_id == scenario_id)
        .order_by(Calculation.id.desc())
        .limit(50)
    ).all()
    return [_calc_out(c) for c in rows]
