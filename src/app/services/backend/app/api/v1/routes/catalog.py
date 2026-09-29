"""Каталог решений: список с фильтрами и фасетами, карточка, статистика.

Каталог — открытый справочник (ТЗ 3.3), поэтому гость видит столько же,
сколько авторизованный пользователь. Различие только в административных
операциях, которые живут в `admin.py`.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import selectinload

from app.api.v1.routes.reference import SOLUTION_LIST_LOAD, serialize_solution
from app.core.db import jsonb_contains
from app.core.deps import DbSession
from app.core.errors import AppError
from app.models import ObjectType, Solution, SolutionType, Vendor
from app.schemas.api import SolutionDetail, SolutionListResponse, SolutionOut

router = APIRouter(prefix="/catalog", tags=["Каталог решений"])

#: Сортировка ограничена белым списком: иначе в ORDER BY можно подставить
#: произвольное выражение и выгрузить всю таблицу одним «ORDER BY».
SORTABLE = {
    "name": Solution.name,
    "price": Solution.unit_price_rub,
    "completeness": Solution.completeness,
    "trl": Solution.trl,
    "payload": Solution.payload_kg,
    "throughput": Solution.throughput_per_hour,
    "created": Solution.created_at,
}


@router.get("", response_model=SolutionListResponse)
def list_solutions(
    db: DbSession,
    search: str | None = Query(default=None, max_length=200),
    object_type: str | None = Query(default=None, description="Код типа объекта"),
    process_code: list[str] | None = Query(default=None),
    solution_type: list[str] | None = Query(default=None, description="Коды типов решений"),
    industry: list[str] | None = Query(
        default=None, description="Отрасли применения (точное совпадение)"
    ),
    vendor_id: list[int] | None = Query(default=None),
    status: list[str] | None = Query(default=None),
    price_source: str | None = Query(default=None),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_completeness: float | None = Query(default=None, ge=0, le=100),
    min_trl: int | None = Query(default=None, ge=1, le=9),
    verified_only: bool = Query(default=False),
    airside_only: bool = Query(default=False, description="Только сертифицированные для аэропорта"),
    medical_only: bool = Query(default=False),
    include_variants: bool = Query(
        default=False,
        description="Показывать ли дубли комплектаций (Дополнения п.6)",
    ),
    sort: str = Query(default="name"),
    desc: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> SolutionListResponse:
    if sort not in SORTABLE:
        raise AppError(
            f"Сортировка «{sort}» не поддерживается.",
            code="bad_sort",
            hint=f"Доступно: {', '.join(sorted(SORTABLE))}.",
        )
    if min_price is not None and max_price is not None and min_price > max_price:
        raise AppError(
            "Минимальная цена больше максимальной.",
            code="bad_range",
            hint="Поменяйте границы местами.",
        )

    filters = []
    if not include_variants:
        # По умолчанию каталог показывает решения, а не комплектации: иначе
        # одна и та же позиция занимает несколько строк подряд.
        filters.append(Solution.is_variant_of_id.is_(None))
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                Solution.name.ilike(pattern),
                Solution.purpose.ilike(pattern),
                Solution.description.ilike(pattern),
                cast(Solution.industry, String).ilike(pattern),
                cast(Solution.scenario_label, String).ilike(pattern),
            )
        )
    if object_type:
        filters.append(
            or_(
                jsonb_contains(Solution.applicable_object_types, [object_type]),
                Solution.applicable_object_types.is_(None),  # назначение не ограничено
            )
        )
    for code in process_code or []:
        filter_ = jsonb_contains(Solution.process_codes, [code])
        if filter_ is not None:
            filters.append(filter_)
    for st in solution_type or []:
        filters.append(
            Solution.solution_type_id.in_(
                select(SolutionType.id).where(SolutionType.code.in_(solution_type))
            )
        )
    if industry:
        # Отрасли в каталоге заведены из «Каталога внедрения» ФЦ БАС, где
        # они названы ровно так же, поэтому сравнение точное, а не по LIKE.
        filters.append(Solution.industry.in_(industry))
    if vendor_id:
        filters.append(Solution.vendor_id.in_(vendor_id))
    if status:
        filters.append(Solution.status.in_(status))
    if price_source:
        filters.append(Solution.price_source == price_source)
    if min_price is not None:
        filters.append(Solution.unit_price_rub >= min_price)
    if max_price is not None:
        filters.append(Solution.unit_price_rub <= max_price)
    if min_completeness is not None:
        filters.append(Solution.completeness >= min_completeness)
    if min_trl is not None:
        filters.append(Solution.trl >= min_trl)
    if verified_only:
        filters.append(Solution.is_verified.is_(True))
    if airside_only:
        filters.append(Solution.airside_certified.is_(True))
    if medical_only:
        filters.append(Solution.medical_sanitation_ready.is_(True))

    total = db.scalar(select(func.count()).select_from(Solution).where(*filters)) or 0
    order = SORTABLE[sort]
    stmt = (
        select(Solution)
        .where(*filters)
        .options(*SOLUTION_LIST_LOAD)
        .order_by(order.desc() if desc else order.asc(), Solution.name.asc())
        .limit(limit)
        .offset(offset)
    )
    rows = db.scalars(stmt).all()

    facets = _facets(db, filters)
    return SolutionListResponse(
        items=[SolutionOut.model_validate(serialize_solution(s)) for s in rows],
        total=total,
        limit=limit,
        offset=offset,
        facets=facets,
    )


def _facets(db: DbSession, filters: list[Any]) -> dict[str, Any]:
    """Значения для фильтров: сколько позиций получится при каждом выборе.

    Считаются по тому же набору фильтров, что и список, — иначе цифры в
    фильтрах не совпадают с результатом и пользователю нечем проверять.
    """
    def counts(column: Any, limit: int = 12) -> list[dict[str, Any]]:
        stmt = (
            select(column, func.count(Solution.id))
            .where(*filters)
            .group_by(column)
            .order_by(func.count(Solution.id).desc())
            .limit(limit)
        )
        return [{"value": v, "count": c} for v, c in db.execute(stmt).all() if v is not None]

    return {
        "status": counts(Solution.status),
        "solution_type": [
            {"value": st.code, "label": st.name, "count": c}
            for st, c in db.execute(
                select(SolutionType, func.count(Solution.id))
                .join(Solution, Solution.solution_type_id == SolutionType.id)
                .where(*filters)
                .group_by(SolutionType.id)
                .order_by(func.count(Solution.id).desc())
            ).all()
        ],
        "vendor": [
            {"value": v.id, "label": v.name, "count": c}
            for v, c in db.execute(
                select(Vendor, func.count(Solution.id))
                .join(Solution, Solution.vendor_id == Vendor.id)
                .where(*filters)
                .group_by(Vendor.id)
                .order_by(func.count(Solution.id).desc())
                .limit(15)
            ).all()
        ],
        "price_source": counts(Solution.price_source),
        "object_type": [
            {
                "value": ot.code,
                "label": ot.name,
                "count": db.scalar(
                    select(func.count())
                    .select_from(Solution)
                    .where(
                        jsonb_contains(Solution.applicable_object_types, [ot.code]),
                        *filters,
                    )
                )
                or 0,
            }
            for ot in db.scalars(select(ObjectType).order_by(ObjectType.order_index)).all()
        ],
    }


@router.get("/stats")
def catalog_stats(db: DbSession) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(Solution)) or 0
    verified = db.scalar(
        select(func.count()).select_from(Solution).where(Solution.is_verified.is_(True))
    ) or 0
    priced = db.scalar(
        select(func.count())
        .select_from(Solution)
        .where(Solution.unit_price_rub.isnot(None))
    ) or 0
    avg_completeness = db.scalar(select(func.avg(Solution.completeness))) or 0
    vendors = db.scalar(select(func.count(func.distinct(Solution.vendor_id)))) or 0
    variants = db.scalar(
        select(func.count()).select_from(Solution).where(Solution.is_variant_of_id.isnot(None))
    ) or 0
    return {
        "total": total,
        "verified": verified,
        "with_price": priced,
        "vendors": vendors,
        "variants": variants,
        "avg_completeness": round(float(avg_completeness), 1),
        "by_status": [
            {"status": s, "count": c}
            for s, c in db.execute(
                select(Solution.status, func.count())
                .group_by(Solution.status)
                .order_by(func.count().desc())
            ).all()
        ],
        "price_coverage_pct": round(priced / total * 100, 1) if total else 0.0,
    }


@router.get("/facets")
def catalog_facets(db: DbSession) -> dict[str, Any]:
    """Значения для панели фильтров: отрасли, типы решений, статусы.

    Отдельный эндпоинт, а не захардкоженный список на фронтенде: при смене
    организатором отраслей или добавлении нового типа решения фильтр обязан
    показать новое значение сам. Иначе позиция попадает в каталог и становится
    недоступной по любому фильтру — молча.

    Считается то же множество, что показывает список по умолчанию, — без
    комплектаций (`is_variant_of_id is None`). Иначе счётчик в скобках
    обещал бы 28 позиций, а по клику открывалось бы 22.
    """
    base = Solution.is_variant_of_id.is_(None)
    industries = [
        {"value": name, "count": count}
        for name, count in db.execute(
            select(Solution.industry, func.count())
            .where(Solution.industry.isnot(None), base)
            .group_by(Solution.industry)
            .order_by(func.count().desc())
        ).all()
    ]
    types = [
        {"value": st.code, "label": st.name, "count": count}
        for st, count in db.execute(
            select(SolutionType, func.count())
            .join(Solution, Solution.solution_type_id == SolutionType.id)
            .where(base)
            .group_by(SolutionType.id)
            .order_by(func.count().desc())
        ).all()
    ]
    statuses = [
        {"value": status, "count": count}
        for status, count in db.execute(
            select(Solution.status, func.count())
            .where(base)
            .group_by(Solution.status)
            .order_by(func.count().desc())
        ).all()
    ]
    without_industry = (
        db.scalar(
            select(func.count())
            .select_from(Solution)
            .where(Solution.industry.is_(None), base)
        )
        or 0
    )
    return {
        "industries": industries,
        "solution_types": types,
        "statuses": statuses,
        # Решения без отрасли иначе не попадают ни под один фильтр «отрасль».
        "without_industry": without_industry,
    }


@router.get("/{solution_id}", response_model=SolutionDetail)
def get_solution(solution_id: uuid.UUID, db: DbSession) -> dict[str, Any]:
    solution = db.scalar(
        select(Solution).where(Solution.id == solution_id).options(*SOLUTION_LIST_LOAD)
    )
    if solution is None:
        raise AppError(
            "Решение не найдено.",
            code="not_found",
            hint="Возможно, оно удалено из каталога. Обновите список.",
            status_code=404,
        )
    data = serialize_solution(solution, detail=True)
    # Варианты комплектации одного решения показываются на карточке,
    # иначе различия между ними негде увидеть.
    data["variants"] = [
        {
            "id": v.id,
            "name": v.name,
            "variant_label": v.variant_label,
            # Колонка Numeric, а схема ждёт float — приводим так же, как
            # в serialize_solution. Раньше здесь стоял несуществующий
            # помощник _f: карточка падала с 500, но только у решений,
            # у которых есть варианты комплектации, — список открывался.
            "unit_price_rub": float(v.unit_price_rub) if v.unit_price_rub is not None else None,
        }
        for v in db.scalars(
            select(Solution)
            .where(Solution.is_variant_of_id == solution.id)
            .order_by(Solution.name)
        ).all()
    ]
    return data
