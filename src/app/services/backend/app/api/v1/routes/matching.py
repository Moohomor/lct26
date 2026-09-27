"""Подбор решений под параметры объекта (ТЗ 3.4).

Логика подбора живёт в `app/services/matching`, роутер только собирает
параметры проекта, вызывает движок и отдаёт результат. Так требования можно
проверить тестами без HTTP.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.core.db import jsonb_contains, jsonb_empty
from app.core.deps import DbSession, LoggedIn, ensure_owner_or_admin
from app.core.errors import AppError
from app.models import ObjectType, Process, Project, ProjectSolution, Solution, SolutionType
from app.schemas.api import MatchRequest, MatchResponse
from app.services.matching import engine as matching
from app.services.matching.requirements import build_requirements, process_metric_code

router = APIRouter(tags=["Подбор решений"])


def _object_type_or_404(db: DbSession, code: str) -> ObjectType:
    ot = db.scalar(select(ObjectType).where(ObjectType.code == code))
    if ot is None:
        raise AppError(
            f"Тип объекта «{code}» неизвестен.",
            code="not_found",
            hint="Допустимые коды: warehouse, airport, medical.",
            status_code=404,
        )
    return ot


def _candidate_solutions(
    db: DbSession,
    object_type: str,
    *,
    solution_type_codes: list[str] | None = None,
    vendor_id: int | None = None,
) -> list[Solution]:
    """Кандидаты: помечены подходящий тип объекта или не ограничены.

    Решения с пустым `applicable_object_types` считаются универсальными и
    участвуют в подборе: не разбирать назначение — не значит запретить
    применение. Процесс здесь не фильтруется: решение может решать смежную
    задачу (транспортёр при перемещении паллет), и решать это должен движок,
    а не предварительный отсев.
    """
    stmt = (
        select(Solution)
        .where(Solution.is_variant_of_id.is_(None))
        .options(
            selectinload(Solution.vendor),
            selectinload(Solution.solution_type),
        )
    )
    stmt = stmt.where(
        or_(
            jsonb_contains(Solution.applicable_object_types, [object_type]),
            jsonb_empty(Solution.applicable_object_types),
        )
    )
    if solution_type_codes:
        stmt = stmt.join(SolutionType, SolutionType.id == Solution.solution_type_id).where(
            SolutionType.code.in_(solution_type_codes)
        )
    if vendor_id is not None:
        stmt = stmt.where(Solution.vendor_id == vendor_id)
    return list(db.scalars(stmt).all())


def _resolve_params(db: DbSession, object_type: str, values: dict[str, Any]) -> dict[str, Any]:
    """Значения параметров объекта: переданные значения плюс значения по умолчанию.

    Без этого подбор по одному лишь `process_code` невозможен: половина
    требований выводится из параметров объекта, и без них проверять нечего.
    """
    from app.models import Parameter

    ot = _object_type_or_404(db, object_type)
    # `default` — вычисляемое свойство (сводит числовую и текстовую колонки
    # к виду формы), фильтровать по нему в SQL нельзя. Отбираем по колонкам.
    defaults = {
        p.code: p.default
        for p in db.scalars(
            select(Parameter).where(
                Parameter.object_type_id == ot.id,
                (Parameter.default_value.isnot(None))
                | (Parameter.default_text.isnot(None)),
            )
        )
    }
    merged = {**defaults, **{k: v for k, v in (values or {}).items() if v is not None}}
    return merged


@router.post("/match", response_model=MatchResponse)
def match_solutions(payload: MatchRequest, db: DbSession) -> dict[str, Any]:
    """Подбор решений для одного процесса объекта."""
    _object_type_or_404(db, payload.object_type)
    params = _resolve_params(db, payload.object_type, payload.parameters)
    solutions = _candidate_solutions(
        db,
        payload.object_type,
        solution_type_codes=payload.solution_type_codes,
        vendor_id=payload.vendor_id,
    )
    result = matching.rank(solutions, payload.object_type, payload.process_code, params)

    items = result["results"]
    if payload.min_score is not None:
        items = [r for r in items if r["score"] >= payload.min_score]
    if not payload.include_rejected:
        items = [r for r in items if r["is_eligible"]]

    eligible = [r for r in items if r["is_eligible"]]
    result["results"] = items[: payload.limit]
    result["summary"] = {
        **result["summary"],
        "eligible_in_page": len(eligible),
        "shown": len(result["results"]),
    }
    result["metric_code"] = process_metric_code(payload.object_type, payload.process_code)
    return result


@router.get("/match")
def match_get(
    db: DbSession,
    object_type: str = Query(description="Код типа объекта"),
    process_code: str = Query(description="Код процесса"),
    parameters: str | None = Query(default=None, description="JSON с параметрами объекта"),
    limit: int = Query(default=20, ge=1, le=200),
    include_rejected: bool = Query(default=True),
    solution_type: list[str] | None = Query(default=None),
    vendor_id: int | None = Query(default=None),
    min_score: float | None = Query(default=None, ge=0, le=100),
) -> dict[str, Any]:
    """GET-вариант подбора — для ссылок вида «посмотреть подбор» и отладки."""
    values: dict[str, Any] = {}
    if parameters:
        try:
            values = json.loads(parameters)
        except json.JSONDecodeError as exc:
            raise AppError(
                f"Параметры переданы не как JSON: {exc.msg}.",
                code="bad_json",
                hint='Пример: {"floor_width_m": 3.2}',
            ) from exc
    return match_solutions(
        MatchRequest(
            object_type=object_type,
            process_code=process_code,
            parameters=values,
            limit=limit,
            include_rejected=include_rejected,
            solution_type_codes=solution_type,
            vendor_id=vendor_id,
            min_score=min_score,
        ),
        db,
    )


@router.get("/match/by-project/{project_id}")
def match_project(
    project_id: uuid.UUID,
    db: DbSession,
    user: LoggedIn,
    process_code: list[str] | None = Query(default=None, description="Пусто — все процессы проекта"),
    limit: int = Query(default=15, ge=1, le=100),
    include_rejected: bool = Query(default=False),
) -> dict[str, Any]:
    """Подбор сразу по нескольким процессам проекта.

    Сводка по процессам, а не один плоский список: иначе решения для разных
    задач сравнивались бы между собой по общему баллу, что бессмысленно.
    """
    project = db.get(Project, project_id)
    if project is None:
        raise AppError("Проект не найден.", code="not_found", status_code=404)
    ensure_owner_or_admin(user, project.user_id)

    codes = list(process_code or project.process_codes or [])
    if not codes:
        raise AppError(
            "В проекте не выбраны процессы.",
            code="no_processes",
            hint="Выберите процессы на шаге описания объекта.",
        )
    params = _resolve_params(db, project.object_type.code, project.parameters or {})
    solutions = _candidate_solutions(db, project.object_type.code)

    per_process = []
    for code in codes:
        ranked = matching.rank(solutions, project.object_type.code, code, params)
        items = ranked["results"]
        if not include_rejected:
            items = [r for r in items if r["is_eligible"]]
        process = db.scalar(select(Process).where(Process.code == code))
        per_process.append(
            {
                "process_code": code,
                "process_name": process.name if process else code,
                "metric_code": process_metric_code(project.object_type.code, code),
                "requirements": ranked["requirements"],
                "peak_demand": ranked["peak_demand"],
                "demand_unit": ranked["demand_unit"],
                "summary": ranked["summary"],
                "results": items[:limit],
            }
        )
    return {
        "project_id": str(project.id),
        "object_type": project.object_type.code,
        "processes": per_process,
        "recommended": _recommend(per_process),
    }


def _recommend(per_process: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Короткий список того, что предложить пользователю в первую очередь.

    Один и тот же робот может закрывать несколько процессов — такие позиции
    поднимаются наверх, потому что покупка одного изделия заменяет несколько.
    """
    by_solution: dict[str, dict[str, Any]] = {}
    for block in per_process:
        for r in block["results"]:
            if not r["is_eligible"]:
                continue
            entry = by_solution.setdefault(
                r["solution_id"],
                {
                    "solution_id": r["solution_id"],
                    "name": r["name"],
                    "vendor": r["vendor"],
                    "solution_type": r["solution_type"],
                    "processes": [],
                    "best_score": 0.0,
                    "unit_price_rub": r["unit_price_rub"],
                    "price_source": r["price_source"],
                    "completeness": r["completeness"],
                },
            )
            entry["processes"].append(
                {"process_code": block["process_code"], "score": r["score"]}
            )
            entry["best_score"] = max(entry["best_score"], r["score"])
    for entry in by_solution.values():
        entry["covers_processes"] = len(entry["processes"])
    return sorted(
        by_solution.values(),
        key=lambda e: (-e["covers_processes"], -e["best_score"]),
    )[:20]


@router.get("/requirements")
def requirements_only(
    db: DbSession,
    object_type: str = Query(),
    process_code: str = Query(),
    parameters: str | None = Query(default=None),
) -> dict[str, Any]:
    """Требования без подбора — чтобы форма показала ограничения до расчёта."""
    values: dict[str, Any] = {}
    if parameters:
        try:
            values = json.loads(parameters)
        except json.JSONDecodeError as exc:
            raise AppError(
                f"Параметры переданы не как JSON: {exc.msg}.", code="bad_json"
            ) from exc
    params = _resolve_params(db, object_type, values)
    reqs, peak, unit = build_requirements(object_type, process_code, params)
    return {
        "object_type": object_type,
        "process_code": process_code,
        "metric_code": process_metric_code(object_type, process_code),
        "peak_demand": peak,
        "demand_unit": unit,
        "requirements": [
            {
                "code": r.code,
                "label": r.label,
                "severity": r.severity,
                "unit": r.unit,
                "minimum": r.minimum,
                "maximum": r.maximum,
                "source_param": r.source_param,
                "text": r.format_text(params),
            }
            for r in reqs
        ],
    }


@router.post("/projects/{project_id}/match", response_model=dict)
def match_and_save(
    project_id: uuid.UUID,
    db: DbSession,
    user: LoggedIn,
    process_code: list[str] | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    save: bool = Query(default=True, description="Добавить лучшие решения в проект"),
) -> dict[str, Any]:
    """Подбор и сохранение результата в подборку проекта.

    Сохраняются только подходящие решения и с пометкой `added_manually=False`:
    происхождение подбора важно отличать от ручного добавления (ТЗ 3.4.4).
    """
    project = db.get(Project, project_id)
    if project is None:
        raise AppError("Проект не найден.", code="not_found", status_code=404)
    ensure_owner_or_admin(user, project.user_id)

    codes = list(process_code or project.process_codes or [])
    if not codes:
        raise AppError("В проекте не выбраны процессы.", code="no_processes")

    params = _resolve_params(db, project.object_type.code, project.parameters or {})
    solutions = _candidate_solutions(db, project.object_type.code)
    added: list[dict[str, Any]] = []

    for code in codes:
        ranked = matching.rank(solutions, project.object_type.code, code, params)
        for r in ranked["results"][:limit]:
            if not r["is_eligible"]:
                continue
            sid = uuid.UUID(r["solution_id"])
            if db.scalar(
                select(ProjectSolution.id).where(
                    ProjectSolution.project_id == project.id,
                    ProjectSolution.solution_id == sid,
                )
            ):
                continue
            link = ProjectSolution(
                project_id=project.id,
                solution_id=sid,
                added_manually=False,
                match_score=r["score"],
                match_reasons={"scores": r["scores"], "checks": r["checks"],
                               "process_code": code, "warnings": r["warnings"]},
            )
            db.add(link)
            added.append(
                {"solution_id": str(sid), "name": r["name"], "score": r["score"],
                 "process_code": code}
            )
    if save:
        db.commit()
    return {"project_id": str(project.id), "added": added, "processed_processes": codes}
