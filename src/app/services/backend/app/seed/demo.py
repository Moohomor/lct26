"""Демонстрационные проекты: по одному на каждый тип объекта.

Зачем они нужны. Первая страница платформы открывается гостю, у гостя нет
проектов, а пустой интерфейс ничего не объясняет. Демо-проекты показывают весь
путь целиком — параметры объекта, подбор решений, три сценария расчёта и
имитацию — на данных организатора, а не на выдуманных числах.

Два свойства, без которых демо бесполезно:

* **Идемпотентность.** Команда `db demo` запускается повторно, в том числе
  при каждом старте приложения. Проекты опознаются по имени и владельцу, а не
  по факту наличия, поэтому повторный запуск не плодит дубликаты.
* **Честность цифр.** Расчёты выполняются тем же движком, что и по запросу
  пользователя. Демо-проект, посчитанный «по-другому», показывал бы жюри
  расхождение между экраном и отчётом.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models import (
    Calculation,
    Normative,
    ObjectType,
    Parameter,
    Process,
    Project,
    ProjectSolution,
    Scenario,
    ScenarioSolution,
    SimulationRun,
    Solution,
    User,
)
from app.services.economics import engine as econ
from app.services.economics.assumptions import apply_overrides, load_assumptions
from app.services.economics.calculator import ScenarioInput, calculate
from app.services.matching import engine as matching
from app.services.simulation.engine import scenario_robots, simulate_scenario


@dataclass(frozen=True)
class DemoSpec:
    """Описание демо-проекта: какие процессы роботизируем и что переопределяем."""

    object_type: str
    name: str
    description: str
    process_codes: tuple[str, ...]
    #: отличия от значений по умолчанию: демо должно выглядеть как реальный
    #: объект, а не как только что открытая пустая форма
    parameter_overrides: dict[str, Any]
    #: одно позитивное и одно осторожное допущение, чтобы было видно, как
    #: сценарий реагирует на переопределение
    assumptions: dict[str, Any]


DEMO_SPECS: tuple[DemoSpec, ...] = (
    DemoSpec(
        object_type="warehouse",
        name="Склад — демо",
        description=(
            "Распределительный склад 18 000 м², внутритранспортные перемещения "
            "паллет между приёмкой, хранением, комплектацией и отгрузкой."
        ),
        # Один процесс, а не три: пилотный проект всегда начинается с одной
        # операции. Если разнести шесть роботов по трём процессам, экономия
        # ФОТ каждого процесса не покроет обслуживание своей единицы техники,
        # и демо честно покажет убыток — но демо должно показывать работу
        # платформы, а не неудачный выбор процессов.
        process_codes=("intra_logistics",),
        parameter_overrides={
            "total_area_m2": 18000.0,
            "active_area_m2": 12000.0,
            "main_aisle_width_m": 3.6,
            "work_aisle_width_m": 2.4,
            "storage_levels": 4,
        },
        assumptions={"labor_cost_multiplier": 0.9, "raas_term_months": 36},
    ),
    DemoSpec(
        object_type="airport",
        name="Аэропорт — демо",
        description=(
            "Зона обслуживания терминала: уборка полезных площадей и перемещение "
            "багажа между зоной сортировки и стендами выдачи."
        ),
        process_codes=("ground_cleaning",),
        parameter_overrides={"terminal_area_m2": 45000.0},
        assumptions={"labor_cost_multiplier": 1.0, "raas_rate_pct": 18.0},
    ),
    DemoSpec(
        object_type="medical",
        name="Медицинское учреждение — демо",
        description=(
            "Стационар на 600 коек: доставка препаратов и расходников по палатам, "
            "уборка помещений, работа склада медикаментов."
        ),
        # Коды процессов совпадают с названиями в справочнике платформы:
        # медицинское учреждение обслуживается доставкой медикаментов
        process_codes=("meds",),
        parameter_overrides={"bed_count": 600, "floors_count": 8},
        assumptions={"labor_cost_multiplier": 1.1, "horizon_years": 7},
    ),
)

#: Сколько решений подбор кладёт в проект на каждый процесс.
#:
#: Два, а не десять: демо должно показывать парк техники, а не каталог.
#: Если отобрать по четыре решения на процесс, каждое получит по одной единице
#: (sizing не применяется к решениям без заявленной производительности), и
#: сценарий превращается в перечень позиций с одинаковым количеством 1 —
#: окупаемость у такого «проекта» отсутствует, и демо ничего не доказывает.
_PER_PROCESS_LIMIT = 2
#: Сколько сценариев и считаем: без этого демо не показывает главного —
#: сравнения покупки с арендой
_SIMULATION_SEED = 20250901


def _object_type(db: Session, code: str) -> ObjectType:
    ot = db.scalar(select(ObjectType).where(ObjectType.code == code))
    if ot is None:
        raise RuntimeError(
            f"Тип объекта «{code}» не загружен. Сначала выполните `db seed`."
        )
    return ot


def _defaults(db: Session, object_type_id: int) -> dict[str, Any]:
    """Значения по умолчанию: с них начинает форма нового проекта."""
    rows = db.scalars(select(Parameter).where(Parameter.object_type_id == object_type_id))
    return {p.code: p.default for p in rows if p.default is not None}


def _check_processes(db: Session, spec: DemoSpec) -> list[str]:
    """Отбрасывает процессы, которых нет в справочнике.

    Демо строится из кода, а не из ручного ввода: если организаторский
    справочник изменится, проект должен собраться из того, что есть, а не
    упасть на неизвестном коде процесса.
    """
    known = {
        p.code
        for p in db.scalars(
            select(Process).where(
                Process.object_type_id == _object_type(db, spec.object_type).id
            )
        )
    }
    return [code for code in spec.process_codes if code in known]


def _solutions_for(
    db: Session, object_type: str, process_codes: list[str], params: dict[str, Any]
) -> list[tuple[Solution, float, str]]:
    """Лучшие решения по каждому процессу: (решение, балл, процесс).

    Отбор идёт напрямую через движок, а не через HTTP: демо должно собираться
    без работающего сервера, иначе его нельзя выполнить на свежей базе.
    """
    candidates = list(
        db.scalars(
            select(Solution)
            .where(Solution.is_variant_of_id.is_(None))
            .options(selectinload(Solution.solution_type), selectinload(Solution.vendor))
        )
    )
    picked: dict[uuid.UUID, tuple[Solution, float, str]] = {}
    for code in process_codes:
        ranked = matching.rank(candidates, object_type, code, params)
        taken = 0
        for r in ranked["results"]:
            if not r["is_eligible"]:
                continue
            sid = uuid.UUID(r["solution_id"])
            if sid in picked:
                continue
            sol = next(s for s in candidates if s.id == sid)
            # Балл решения из другого процесса высок и при этом бессмысленен:
            # уборщик наберёт много баллов за габариты, но не выполнит ни одной
            # перевозки, и экономия ФОТ по процессу останется нулевой. Поэтому
            # кандидат обязан быть применим к процессу, для которого его берут.
            if code not in (sol.process_codes or []):
                continue
            picked[sid] = (sol, float(r["score"]), code)
            taken += 1
            if taken >= _PER_PROCESS_LIMIT:
                break
    return list(picked.values())


def _scenario_items(
    db: Session,
    spec: DemoSpec,
    solutions: list[tuple[Solution, float, str]],
    params: dict[str, Any],
) -> list[tuple[uuid.UUID, int]]:
    """Количество единиц по sizing — так же, как это делает расчёт пользователя.

    Число выводится из пиковой потребности объекта, а не берётся «на глаз»:
    демо обязано показывать тот же путь `auto`, которым пойдёт человек,
    иначе окупаемость в демо и в отчёте разойдётся.
    """
    from app.services.economics.calculator import auto_quantity

    assumptions = load_assumptions(db, settings.calc_model_version)
    apply_overrides(assumptions, spec.assumptions)
    items: list[tuple[uuid.UUID, int]] = []
    for sol, _score, _code in solutions:
        quantity, _detail = auto_quantity(
            sol, assumptions, spec.object_type, list(spec.process_codes), params
        )
        if quantity and quantity > 0:
            items.append((sol.id, int(quantity)))
    return items


def _store_calculation(
    db: Session, scenario: Scenario, user: User, payload: ScenarioInput, result: dict[str, Any]
) -> Calculation:
    source = result.get(scenario.kind) or result.get(econ.KIND_PURCHASE) or {}
    calc = Calculation(
        scenario_id=scenario.id,
        user_id=user.id,
        kind=scenario.kind,
        model_version=result["meta"]["model_version"],
        catalog_version=result["meta"].get("catalog_version"),
        capex_total=_dec(source.get("capex", {}).get("total")),
        annual_effect=_dec(source.get("effect", {}).get("net_annual_cash")),
        payback_years=_dec(source.get("payback_years")),
        input_snapshot={
            "object_type": payload.object_type,
            "process_codes": payload.process_codes,
            "params": payload.params,
            "items": [[str(sid), q] for sid, q in payload.items],
            "assumptions_override": payload.assumptions_override,
            "horizon_years": payload.horizon_years,
            "quantity_mode": "auto",
        },
        result=result,
        duration_ms=result["meta"].get("duration_ms"),
    )
    db.add(calc)
    return calc


def _dec(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(round(float(value), 2)))
    except (TypeError, ValueError):
        return None


def _build_one(db: Session, user: User, spec: DemoSpec, *, force: bool) -> dict[str, Any]:
    existing = db.scalar(
        select(Project).where(Project.user_id == user.id, Project.name == spec.name)
    )
    if existing is not None:
        if not force:
            return {
                "object_type": spec.object_type,
                "project": spec.name,
                "status": "уже был создан",
                "id": str(existing.id),
            }
        # Пересборка начинается с чистого листа: иначе решения, отобранные
        # прежним составом каталога, остались бы в подборке навсегда.
        db.delete(existing)
        db.flush()

    object_type = _object_type(db, spec.object_type)
    params = {**_defaults(db, object_type.id), **spec.parameter_overrides}
    params = {k: v for k, v in params.items() if v is not None}
    process_codes = _check_processes(db, spec)
    if not process_codes:
        return {"object_type": spec.object_type, "status": "нет процессов для демо"}

    solutions = _solutions_for(db, spec.object_type, process_codes, params)
    if not solutions:
        return {"object_type": spec.object_type, "status": "подбор ничего не вернул"}

    project = Project(
        user_id=user.id,
        object_type_id=object_type.id,
        name=spec.name,
        description=spec.description,
        organization=user.organization or "Демонстрационный набор",
        status="draft",
        parameters=params,
        process_codes=process_codes,
        params_version=_params_version(db, object_type.id),
        is_demo=True,
    )
    db.add(project)
    db.flush()

    for sol, score, code in solutions:
        db.add(
            ProjectSolution(
                project_id=project.id,
                solution_id=sol.id,
                added_manually=False,
                match_score=score,
                match_reasons={"process_code": code, "source": "demo"},
            )
        )

    items = _scenario_items(db, spec, solutions, params)
    created: list[dict[str, Any]] = []
    if items:
        for order, (kind, title) in enumerate(
            (
                (econ.KIND_PURCHASE, "Покупка оборудования"),
                (econ.KIND_RAAS, "Роботизация как услуга (RaaS)"),
            )
        ):
            scenario = Scenario(
                project_id=project.id,
                name=title,
                kind=kind,
                description=(
                    spec.assumptions and
                    "Допущения переопределены: " + ", ".join(
                        f"{k} = {v}" for k, v in spec.assumptions.items()
                    )
                )
                or None,
                assumptions=spec.assumptions,
                horizon_years=int(spec.assumptions.get("horizon_years", 5)),
                order_index=order,
            )
            db.add(scenario)
            db.flush()
            for sid, quantity in items:
                db.add(
                    ScenarioSolution(
                        scenario_id=scenario.id, solution_id=sid, quantity=quantity
                    )
                )
            db.flush()

            payload = ScenarioInput(
                object_type=spec.object_type,
                object_type_name=object_type.name,
                process_codes=process_codes,
                params=params,
                items=items,
                assumptions_override=dict(spec.assumptions),
                horizon_years=scenario.horizon_years,
                kind=kind,
            )
            result = calculate(db, payload, with_sensitivity=True)
            _store_calculation(db, scenario, user, payload, result)
            scenario.last_calculated_at = datetime.now(UTC)

            if kind == econ.KIND_PURCHASE:
                _simulate(db, scenario, project, object_type, spec, params, result)

            source = result.get(kind) or {}
            # TCO считается сразу по трём сценариям и лежит на верхнем уровне
            # результата, внутри отдельного сценария его нет.
            tco_block = ((result.get("tco") or {}).get("scenarios") or {}).get(kind) or {}
            created.append(
                {
                    "kind": kind,
                    "positions": len(items),
                    "capex": _round(source.get("capex", {}).get("total")),
                    "opex_per_year": _round(source.get("opex", {}).get("total")),
                    "net_annual_cash": _round(source.get("effect", {}).get("net_annual_cash")),
                    "payback_years": source.get("payback_years"),
                    "tco": _round(tco_block.get("total")),
                }
            )

    project.status = "calculated"
    db.commit()
    return {
        "object_type": spec.object_type,
        "project": spec.name,
        "status": "создан",
        "id": str(project.id),
        "processes": process_codes,
        "solutions": len(solutions),
        "scenarios": created,
    }


def _simulate(
    db: Session,
    scenario: Scenario,
    project: Project,
    object_type: ObjectType,
    spec: DemoSpec,
    params: dict[str, Any],
    result: dict[str, Any],
) -> None:
    """Имитация для сценария покупки: раскладка, KPI и расписание."""
    db.refresh(scenario)
    robots = scenario_robots(scenario)
    if not robots:
        return
    assumptions = load_assumptions(db, settings.calc_model_version)
    apply_overrides(assumptions, spec.assumptions)
    try:
        outcome = simulate_scenario(
            object_type=object_type.code,
            params=params,
            process_codes=list(project.process_codes or []),
            robots=robots,
            assumptions=assumptions,
            seed=_SIMULATION_SEED,
            include_schedule=True,
        )
    except Exception as exc:  # noqa: BLE001 — демо не должно падать из-за имитации
        db.add(
            SimulationRun(
                scenario_id=scenario.id,
                status="failed",
                progress=0,
                error_message=str(exc)[:500],
            )
        )
        return
    db.add(
        SimulationRun(
            scenario_id=scenario.id,
            status="done",
            progress=100,
            speed_factor=Decimal("1"),
            layout=outcome.layout,
            kpi=outcome.kpi,
            schedule=outcome.schedule,
            duration_ms=outcome.duration_ms,
            started_at=datetime.now(UTC),
            finished_at=datetime.now(UTC),
        )
    )
    _ = result  # расчёт нужен вызывающему коду, здесь — только как гарантия порядка


def _params_version(db: Session, object_type_id: int) -> str:
    count = (
        db.scalar(
            select(func.count())
            .select_from(Parameter)
            .where(Parameter.object_type_id == object_type_id)
        )
        or 0
    )
    return f"{object_type_id}-{count}"


def _round(value: Any) -> float | None:
    return round(float(value), 2) if value is not None else None


def build_demo_projects(
    db: Session, *, email: str | None = None, force: bool = False
) -> dict[str, Any]:
    """Создаёт демо-проекты владельцу `email` (по умолчанию — демо-пользователю).

    Идемпотентно: повторный вызов без `force` ничего не меняет и возвращает
    список уже созданных проектов.
    """
    from app.seed.seed import DEMO_USER_EMAIL

    user = db.scalar(select(User).where(User.email == (email or DEMO_USER_EMAIL)))
    if user is None:
        raise RuntimeError(
            f"Пользователь {email or DEMO_USER_EMAIL} не найден. Сначала выполните `db seed`."
        )

    results = [_build_one(db, user, spec, force=force) for spec in DEMO_SPECS]
    return {
        "user": user.email,
        "force": force,
        "projects": results,
        "total": len(results),
        "normatives": db.scalar(select(func.count()).select_from(Normative)) or 0,
    }
