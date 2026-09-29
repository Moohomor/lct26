"""Справочники: типы объектов, параметры, процессы, типы решений, вендоры (ТЗ 3.2).

Открыты для гостя: без авторизации платформа должна давать осмысленный ответ,
иначе посетитель увидит пустой экран вместо объяснения, что делать дальше.
"""

from __future__ import annotations

from pathlib import Path

from typing import Annotated, Any

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.core.deps import DbSession
from app.core.errors import AppError
from app.models import (
    DataSource,
    Normative,
    ObjectType,
    Parameter,
    ParameterGroup,
    Process,
    Solution,
    SolutionType,
    Vendor,
)
from app.schemas.api import (
    DataSourceOut,
    NormativeOut,
    ObjectTypeDetail,
    ObjectTypeOut,
    ParameterGroupOut,
    ParameterOut,
    ProcessOut,
    SolutionTypeOut,
    VendorOut,
)

router = APIRouter(tags=["Справочники"])


def _get_object_type(db: DbSession, code: str) -> ObjectType:
    object_type = db.scalar(select(ObjectType).where(ObjectType.code == code))
    if object_type is None:
        raise AppError(
            f"Тип объекта «{code}» неизвестен.",
            code="not_found",
            hint="Допустимые коды: warehouse, airport, medical.",
            status_code=404,
        )
    return object_type


def _f(value: Any) -> float | None:
    return float(value) if value is not None else None


def _param_out(p: Parameter) -> dict[str, Any]:
    """Плоский вид параметра: то, из чего форма собирает поле ввода.

    Значение по умолчанию приводится к типу поля (`bool` — настоящий bool,
    `enum` — строка), иначе фронтенд будет гадать, как это отображать.
    """
    return {
        "id": p.id,
        "object_type_id": p.object_type_id,
        "group_id": p.group_id,
        "code": p.code,
        "name": p.name,
        "unit": p.unit,
        "value_type": p.value_type,
        "default": p.default,
        "min_value": _f(p.min_value),
        "max_value": _f(p.max_value),
        "step": _f(p.step),
        "options": p.options,
        "required": p.required,
        "is_affecting_economics": p.is_affecting_economics,
        "is_demo": p.is_demo,
        "order_index": p.order_index,
        "help_text": p.help_text,
        "note": p.note,
        "group_code": p.group.code if p.group else None,
        "group_name": p.group.name if p.group else None,
    }


def _group_params(params: list[Parameter], groups: list[ParameterGroup]) -> list[dict[str, Any]]:
    """Раскладывает параметры по группам, сохраняя порядок групп и полей."""
    by_code = {g.code: g for g in groups}
    buckets: dict[str, list[dict[str, Any]]] = {}
    for p in params:
        buckets.setdefault(p.group.code if p.group else "_other", []).append(_param_out(p))
    out = []
    for code, items in buckets.items():
        group = by_code.get(code)
        out.append(
            {
                "code": code,
                "name": group.name if group else ("Прочие параметры" if code == "_other" else code),
                "order_index": group.order_index if group else 999,
                "parameters": sorted(items, key=lambda x: (x["order_index"], x["name"])),
            }
        )
    return sorted(out, key=lambda g: (g["order_index"], g["name"]))


# ── Типы объектов ────────────────────────────────────────────────────────────


def _object_type_out(
    ot: ObjectType, *, process_count: int = 0, param_count: int = 0
) -> dict[str, Any]:
    return {
        "id": ot.id,
        "code": ot.code,
        "name": ot.name,
        "description": ot.description,
        "icon": ot.icon,
        "order_index": ot.order_index,
        "is_active": ot.is_active,
        "process_count": process_count,
        "parameter_count": param_count,
    }


@router.get("/object-types", response_model=list[ObjectTypeOut])
def list_object_types(db: DbSession) -> list[dict[str, Any]]:
    rows = db.execute(
        select(
            ObjectType,
            func.count(func.distinct(Process.id)),
            func.count(func.distinct(Parameter.id)),
        )
        .outerjoin(Process, Process.object_type_id == ObjectType.id)
        .outerjoin(Parameter, Parameter.object_type_id == ObjectType.id)
        .group_by(ObjectType.id)
        .order_by(ObjectType.order_index, ObjectType.id)
    ).all()
    return [_object_type_out(ot, process_count=pc, param_count=rc) for ot, pc, rc in rows]


@router.get("/object-types/{code}", response_model=ObjectTypeDetail)
def get_object_type(code: str, db: DbSession) -> dict[str, Any]:
    ot = _get_object_type(db, code)
    processes = db.scalars(
        select(Process)
        .where(Process.object_type_id == ot.id)
        .order_by(Process.order_index, Process.name)
    ).all()
    params = list(
        db.scalars(
            select(Parameter)
            .where(Parameter.object_type_id == ot.id)
            .options(selectinload(Parameter.group))
            .order_by(Parameter.order_index, Parameter.name)
        ).all()
    )
    groups = list(
        db.scalars(
            select(ParameterGroup)
            .where(ParameterGroup.object_type_id == ot.id)
            .order_by(ParameterGroup.order_index)
        ).all()
    )
    return {
        **_object_type_out(ot, process_count=len(processes), param_count=len(params)),
        "processes": [ProcessOut.model_validate(p) for p in processes],
        "parameter_groups": _group_params(params, groups),
    }


@router.get("/object-types/{code}/parameters", response_model=list[ParameterOut])
def list_parameters(
    code: str,
    db: DbSession,
    group_code: str | None = Query(default=None, description="Фильтр по группе"),
    affecting_economics: Annotated[bool | None, Query()] = None,
    required_only: bool = Query(default=False),
) -> list[dict[str, Any]]:
    ot = _get_object_type(db, code)
    stmt = (
        select(Parameter)
        .where(Parameter.object_type_id == ot.id)
        .options(selectinload(Parameter.group))
    )
    if group_code:
        stmt = stmt.join(ParameterGroup).where(ParameterGroup.code == group_code)
    if affecting_economics is not None:
        stmt = stmt.where(Parameter.is_affecting_economics.is_(affecting_economics))
    if required_only:
        stmt = stmt.where(Parameter.required.is_(True))
    stmt = stmt.order_by(Parameter.order_index, Parameter.name)
    return [_param_out(p) for p in db.scalars(stmt)]


@router.get("/object-types/{code}/parameters/defaults")
def parameter_defaults(code: str, db: DbSession) -> dict[str, Any]:
    """Значения по умолчанию — то, с чего начинает форма нового проекта."""
    ot = _get_object_type(db, code)
    params = db.scalars(
        select(Parameter)
        .where(
            Parameter.object_type_id == ot.id,
            (Parameter.default_value.isnot(None)) | (Parameter.default_text.isnot(None)),
        )
        .order_by(Parameter.order_index)
    ).all()
    return {
        "object_type": ot.code,
        "object_type_name": ot.name,
        "count": len(params),
        "values": {p.code: p.default for p in params},
        "economics_parameters": [p.code for p in params if p.is_affecting_economics],
        "required_parameters": [p.code for p in params if p.required],
    }


# ── Процессы ────────────────────────────────────────────────────────────────


@router.get("/processes", response_model=list[ProcessOut])
def list_processes(
    db: DbSession,
    object_type: str | None = Query(default=None, description="Код типа объекта"),
) -> list[ProcessOut]:
    stmt = select(Process).order_by(Process.order_index, Process.name)
    if object_type:
        stmt = (
            stmt.join(ObjectType, ObjectType.id == Process.object_type_id)
            .where(ObjectType.code == object_type)
            .order_by(ObjectType.order_index, Process.order_index, Process.name)
        )
    return [ProcessOut.model_validate(p) for p in db.scalars(stmt)]


# ── Типы решений и вендоры ─────────────────────────────────────────────────


@router.get("/solution-types", response_model=list[SolutionTypeOut])
def list_solution_types(db: DbSession) -> list[SolutionTypeOut]:
    rows = db.execute(
        select(SolutionType, func.count(Solution.id))
        .outerjoin(Solution, Solution.solution_type_id == SolutionType.id)
        .group_by(SolutionType.id)
        .order_by(SolutionType.order_index, SolutionType.id)
    ).all()
    return [
        {**SolutionTypeOut.model_validate(st).model_dump(), "solution_count": cnt}
        for st, cnt in rows
    ]


@router.get("/vendors", response_model=list[VendorOut])
def list_vendors(
    db: DbSession,
    search: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[VendorOut]:
    stmt = (
        select(Vendor, func.count(Solution.id))
        .outerjoin(Solution, Solution.vendor_id == Vendor.id)
        .group_by(Vendor.id)
        .order_by(Vendor.name)
    )
    if search:
        stmt = stmt.where(Vendor.name.ilike(f"%{search.strip()}%"))
    stmt = stmt.limit(limit)
    return [
        {**VendorOut.model_validate(v).model_dump(), "solution_count": cnt}
        for v, cnt in db.execute(stmt).all()
    ]


# ── Нормативы: чтение для всех, правка — администратору ────────────────────


@router.get("/normatives", response_model=list[NormativeOut])
def list_normatives(
    db: DbSession,
    category: str | None = Query(default=None),
    editable_only: bool = Query(default=False),
) -> list[dict[str, Any]]:
    stmt = select(Normative).order_by(Normative.category, Normative.name)
    if category:
        stmt = stmt.where(Normative.category == category)
    if editable_only:
        stmt = stmt.where(Normative.is_editable.is_(True))
    return [
        {
            "id": n.id,
            "code": n.code,
            "name": n.name,
            "value": float(n.value),
            "unit": n.unit,
            "category": n.category,
            "value_type": n.value_type,
            "min_value": _f(n.min_value),
            "max_value": _f(n.max_value),
            "is_editable": n.is_editable,
            "source": n.source,
            "note": n.note,
            "model_version": n.model_version,
            "version": n.version,
        }
        for n in db.scalars(stmt)
    ]


@router.get("/normatives/categories")
def normative_categories(db: DbSession) -> list[dict[str, Any]]:
    rows = db.execute(
        select(Normative.category, func.count(Normative.id))
        .group_by(Normative.category)
        .order_by(Normative.category)
    ).all()
    return [{"code": c, "name": c, "count": cnt} for c, cnt in rows]


@router.get("/data-sources", response_model=list[DataSourceOut])
def list_data_sources(db: DbSession) -> list[dict[str, Any]]:
    return [
        {
            "id": d.id,
            "name": d.name,
            "url": d.url,
            "kind": d.kind,
            "retrieved_at": d.retrieved_at.isoformat() if d.retrieved_at else None,
            "is_verified": d.is_verified,
            "note": d.note,
        }
        for d in db.scalars(select(DataSource).order_by(DataSource.name))
    ]


@router.get("/parameter-groups", response_model=list[ParameterGroupOut])
def list_parameter_groups(
    db: DbSession, object_type: str | None = Query(default=None)
) -> list[dict[str, Any]]:
    params_stmt = select(Parameter).options(selectinload(Parameter.group))
    groups_stmt = select(ParameterGroup).order_by(ParameterGroup.order_index)
    if object_type:
        ot = _get_object_type(db, object_type)
        params_stmt = params_stmt.where(Parameter.object_type_id == ot.id)
        groups_stmt = groups_stmt.where(ParameterGroup.object_type_id == ot.id)
    else:
        params_stmt = params_stmt.order_by(Parameter.object_type_id, Parameter.order_index)
    return _group_params(list(db.scalars(params_stmt).all()), list(db.scalars(groups_stmt).all()))


#: Связи для списка каталога грузятся одним запросом: иначе на каждой строке
#: делается отдельный SELECT (N+1), что на 226 позициях заметно.
SOLUTION_LIST_LOAD = (
    selectinload(Solution.vendor),
    selectinload(Solution.solution_type),
    selectinload(Solution.data_source),
)


def _opt_float(value: Any) -> float | None:
    """Decimal/None → float/None: в JSON числа должны быть числами."""
    return float(value) if value is not None else None


def serialize_solution(s: Solution, *, detail: bool = False) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": s.id,
        "name": s.name,
        "vendor": (
            {
                "id": s.vendor.id,
                "name": s.vendor.name,
                "country": s.vendor.country,
                "region": s.vendor.region,
                "website": s.vendor.website,
            }
            if s.vendor
            else None
        ),
        "solution_type": (
            {
                "id": s.solution_type.id,
                "code": s.solution_type.code,
                "name": s.solution_type.name,
                "is_mobile": s.solution_type.is_mobile,
                "requires_passage": s.solution_type.requires_passage,
                "passage_margin_m": float(s.solution_type.passage_margin_m)
                if s.solution_type.passage_margin_m is not None
                else None,
            }
            if s.solution_type
            else None
        ),
        # photo_file хранится относительно app/assets ("solutions/x.jpg"),
        # а статика смонтирована на каталог solutions — в URL попадает
        # только имя файла.
        "photo_url": f"/static/{Path(s.photo_file).name}" if s.photo_file else None,
        "status": s.status,
        "trl": s.trl,
        "purpose": s.purpose,
        "description": s.description,
        "industry": s.industry,
        "region": s.region,
        "applicable_object_types": s.applicable_object_types,
        "process_codes": s.process_codes,
        "restrictions": s.restrictions,
        "infrastructure_requirements": s.infrastructure_requirements,
        "airside_certified": s.airside_certified,
        "medical_sanitation_ready": s.medical_sanitation_ready,
        "unit_price_rub": float(s.unit_price_rub) if s.unit_price_rub is not None else None,
        "price_source": s.price_source,
        "completeness": float(s.completeness),
        "is_verified": s.is_verified,
        "is_variant_of_id": s.is_variant_of_id,
        "variant_label": s.variant_label,
        "data_source": (
            {
                "id": s.data_source.id,
                "name": s.data_source.name,
                "url": s.data_source.url,
                "kind": s.data_source.kind,
                "is_verified": s.data_source.is_verified,
            }
            if s.data_source
            else None
        ),
        "specs_updated_at": s.specs_updated_at.isoformat() if s.specs_updated_at else None,
    }
    if not detail:
        return base
    base.update(
        {
            "payload_kg": _opt_float(s.payload_kg),
            "own_weight_kg": _opt_float(s.own_weight_kg),
            "length_m": _opt_float(s.length_m),
            "width_m": _opt_float(s.width_m),
            "height_m": _opt_float(s.height_m),
            "min_passage_width_m": _opt_float(s.min_passage_width_m),
            "lift_height_m": _opt_float(s.lift_height_m),
            "max_speed_mps": _opt_float(s.max_speed_mps),
            "throughput_per_hour": _opt_float(s.throughput_per_hour),
            "throughput_unit": s.throughput_unit,
            "autonomy_hours": _opt_float(s.autonomy_hours),
            "charge_time_min": _opt_float(s.charge_time_min),
            "positioning_accuracy_mm": _opt_float(s.positioning_accuracy_mm),
            "navigation_types": s.navigation_types,
            "min_temp_c": _opt_float(s.min_temp_c),
            "max_temp_c": _opt_float(s.max_temp_c),
            "max_noise_dba": _opt_float(s.max_noise_dba),
            "max_floor_roughness_mm": _opt_float(s.max_floor_roughness_mm),
            "charge_power_kw": _opt_float(s.charge_power_kw),
            "battery_capacity_kwh": _opt_float(s.battery_capacity_kwh),
            "battery_lifetime_years": _opt_float(s.battery_lifetime_years),
            "lifetime_years": _opt_float(s.lifetime_years),
            "software_price_rub": _opt_float(s.software_price_rub),
            "implementation_price_rub": _opt_float(s.implementation_price_rub),
            "service_rate_pct": _opt_float(s.service_rate_pct),
            "purchase_model": s.purchase_model,
            "scenario_label": s.scenario_label,
            "cases": s.cases,
            "market_potential": _opt_float(s.market_potential),
            "catalog_id": str(s.catalog_id) if s.catalog_id else None,
            "raw": s.raw,
        }
    )
    return base
