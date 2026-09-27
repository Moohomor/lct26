"""Административные операции (ТЗ 3.5.8, 3.2.4).

Всё, что меняет справочники, защищено ролью администратора и пишется в журнал
аудита: правка коэффициента меняет цифры у всех, кто когда-либо посчитал по
старой модели, и без следа это не объяснить.
"""

from __future__ import annotations

import time
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import APIRouter, Query, status
from sqlalchemy import func, select

from app.core.deps import AdminUser, DbSession
from app.core.errors import AppError
from app.models import (
    AuditLog,
    Calculation,
    Normative,
    ObjectType,
    Parameter,
    ParameterGroup,
    Project,
    Solution,
    User,
)
from app.schemas.api import (
    NormativeOut,
    NormativeUpdate,
    ParameterCreate,
    ParameterOut,
    ParameterUpdate,
    SeedRunOut,
    UserAdminOut,
    UserUpdateAdmin,
)

router = APIRouter(prefix="/admin", tags=["Администрирование"])


def _audit(
    db: DbSession,
    user: User,
    action: str,
    entity: str,
    entity_id: str | None = None,
    before: Any = None,
    after: Any = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user.id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            before=before,
            after=after,
        )
    )


def _normative_out(n: Normative) -> dict[str, Any]:
    return {
        "id": n.id,
        "code": n.code,
        "name": n.name,
        "value": float(n.value),
        "unit": n.unit,
        "category": n.category,
        "value_type": n.value_type,
        "min_value": float(n.min_value) if n.min_value is not None else None,
        "max_value": float(n.max_value) if n.max_value is not None else None,
        "is_editable": n.is_editable,
        "source": n.source,
        "note": n.note,
        "model_version": n.model_version,
        "version": n.version,
    }


# ── Нормативы ──────────────────────────────────────────────────────────────


@router.get("/normatives", response_model=list[NormativeOut])
def list_normatives_admin(
    db: DbSession, user: AdminUser, category: str | None = Query(default=None)
) -> list[dict[str, Any]]:
    stmt = select(Normative).order_by(Normative.category, Normative.name)
    if category:
        stmt = stmt.where(Normative.category == category)
    return [_normative_out(n) for n in db.scalars(stmt)]


@router.patch("/normatives/{normative_id}", response_model=NormativeOut)
def update_normative(
    normative_id: int, payload: NormativeUpdate, db: DbSession, user: AdminUser
) -> NormativeOut:
    """Правка коэффициента расчётной модели.

    Проверяется диапазон из самого норматива: если администратор задал
    минимальное значение 3, то 2 — опечатка, а не «другое допущение».
    """
    normative = db.get(Normative, normative_id)
    if normative is None:
        raise AppError("Норматив не найден.", code="not_found", status_code=404)
    if not normative.is_editable:
        raise AppError(
            f"Норматив «{normative.name}» не редактируется через платформу.",
            code="not_editable",
            hint="Он приходит из файла организатора; измените файл и переимпортируйте.",
        )

    before = {"value": str(normative.value), "note": normative.note}
    if payload.value is not None:
        value = _coerce_normative(normative, payload.value)
        if normative.min_value is not None and value < Decimal(str(normative.min_value)):
            raise AppError(
                f"Значение ниже допустимого минимума {normative.min_value} {normative.unit or ''}.",
                code="out_of_range",
                hint=f"Для этого параметра допустим диапазон "
                f"{normative.min_value}…{normative.max_value}.",
            )
        if normative.max_value is not None and value > Decimal(str(normative.max_value)):
            raise AppError(
                f"Значение выше допустимого максимума {normative.max_value} {normative.unit or ''}.",
                code="out_of_range",
                hint=f"Для этого параметра допустим диапазон "
                f"{normative.min_value}…{normative.max_value}.",
            )
        normative.value = value
        # Версия растёт: снимки расчётов ссылаются на версию модели, и по ней
        # можно понять, каким нормативом посчитаны сохранённые цифры.
        normative.version = (normative.version or 1) + 1
    if payload.note is not None:
        normative.note = payload.note

    _audit(
        db, user, "update", "normative", str(normative.id),
        before=before,
        after={"value": str(normative.value), "note": normative.note,
               "version": normative.version},
    )
    db.commit()
    db.refresh(normative)
    return _normative_out(normative)


def _coerce_normative(normative: Normative, value: Any) -> Decimal:
    try:
        if normative.value_type in ("number", "percent"):
            return Decimal(str(value).replace(",", "."))
        if normative.value_type in ("integer", "bool"):
            return Decimal(int(float(str(value).replace(",", "."))))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise AppError(
            f"Значение «{value}» не является {normative.value_type}.",
            code="bad_value",
        ) from exc
    raise AppError(
        f"Норматив типа «{normative.value_type}» нельзя изменить числом.",
        code="bad_value",
        hint="Текстовые нормативы меняются в файле-источнике и переимпортируются.",
    )


@router.post("/normatives/reset")
def reset_normatives(db: DbSession, user: AdminUser) -> dict[str, Any]:
    """Возвращает нормативы к значениям из файла организатора.

    Ручная правка коэффициента — это осознанное решение под конкретный
    расчёт. Когда оно теряет смысл (сменились условия, пришли новые данные
    организатора), способ вернуться к исходным значениям должен быть.
    """
    from app.seed.normatives_seed import by_code

    restored: list[str] = []
    for code, defn in by_code().items():
        normative = db.scalar(select(Normative).where(Normative.code == code))
        if normative is None:
            continue
        if Decimal(str(normative.value)) == defn.value:
            continue
        _audit(
            db, user, "reset", "normative", str(normative.id),
            before={"value": str(normative.value), "version": normative.version},
            after={"value": str(defn.value), "version": (normative.version or 1) + 1},
        )
        normative.value = defn.value
        normative.version = (normative.version or 1) + 1
        restored.append(code)
    db.commit()
    return {
        "ok": True,
        "restored": len(restored),
        "codes": restored,
        "total": len(by_code()),
    }


# ── Параметры объектов ─────────────────────────────────────────────────────


def _param_out(p: Parameter) -> dict[str, Any]:
    return {
        "id": p.id,
        "object_type_id": p.object_type_id,
        "group_id": p.group_id,
        "code": p.code,
        "name": p.name,
        "unit": p.unit,
        "value_type": p.value_type,
        "default": p.default,
        "min_value": float(p.min_value) if p.min_value is not None else None,
        "max_value": float(p.max_value) if p.max_value is not None else None,
        "step": float(p.step) if p.step is not None else None,
        "options": p.options,
        "required": p.required,
        "is_affecting_economics": p.is_affecting_economics,
        "is_demo": p.is_demo,
        "order_index": p.order_index,
        "help_text": p.help_text,
        "note": p.note,
    }


def _find_group(db: DbSession, object_type_id: int, code: str | None) -> ParameterGroup | None:
    if not code:
        return None
    return db.scalar(
        select(ParameterGroup).where(
            ParameterGroup.object_type_id == object_type_id, ParameterGroup.code == code
        )
    )


def _split_default(value_type: str, value: Any) -> tuple[Any, Any]:
    """Раскладывает значение по умолчанию на числовую и текстовую части.

    В модели они разнесены по двум колонкам: перечисление и «Да/Нет» хранятся
    текстом, число — числом. Смешивать их в одной колонке нельзя, иначе форма
    получит строку «12» там, где ждёт число, и сравнение с диапазоном упадёт.
    """
    if value is None:
        return None, None
    if value_type in ("number", "percent", "integer"):
        try:
            number = float(value) if value_type != "integer" else int(float(value))
        except (TypeError, ValueError):
            return None, str(value)
        return number, None
    if value_type == "bool":
        return None, "Да" if value else "Нет"
    return None, str(value)


@router.post(
    "/object-types/{object_type_code}/parameters",
    response_model=ParameterOut,
    status_code=status.HTTP_201_CREATED,
)
def create_parameter(
    object_type_code: str, payload: ParameterCreate, db: DbSession, user: AdminUser
) -> dict[str, Any]:
    object_type = db.scalar(select(ObjectType).where(ObjectType.code == object_type_code))
    if object_type is None:
        raise AppError("Тип объекта не найден.", code="not_found", status_code=404)
    if db.scalar(
        select(Parameter.id).where(
            Parameter.object_type_id == object_type.id, Parameter.code == payload.code
        )
    ):
        raise AppError(
            f"Параметр «{payload.code}» уже существует.",
            code="duplicate",
            hint="Изменить существующий можно методом PATCH.",
            status_code=409,
        )
    group = _find_group(db, object_type.id, payload.group_code)
    max_order = db.scalar(
        select(func.max(Parameter.order_index)).where(
            Parameter.object_type_id == object_type.id
        )
    ) or 0
    default_value, default_text = _split_default(payload.value_type, payload.default)
    param = Parameter(
        object_type_id=object_type.id,
        group_id=group.id if group else None,
        code=payload.code,
        name=payload.name,
        value_type=payload.value_type,
        unit=payload.unit,
        default_value=default_value,
        default_text=default_text,
        min_value=payload.min_value,
        max_value=payload.max_value,
        step=payload.step,
        options=payload.options,
        required=payload.required,
        is_affecting_economics=payload.is_affecting_economics,
        help_text=payload.help_text,
        # Новый параметр введён администратором, а не приехал из файла
        # организатора — это различие видно в интерфейсе справочника.
        is_demo=False,
        order_index=int(max_order) + 1,
    )
    db.add(param)
    db.flush()
    _audit(db, user, "create", "parameter", payload.code, after=payload.model_dump())
    db.commit()
    db.refresh(param)
    return _param_out(param)


@router.patch(
    "/object-types/{object_type_code}/parameters/{code}", response_model=ParameterOut
)
def update_parameter(
    object_type_code: str, code: str, payload: ParameterUpdate, db: DbSession, user: AdminUser
) -> dict[str, Any]:
    object_type = db.scalar(select(ObjectType).where(ObjectType.code == object_type_code))
    if object_type is None:
        raise AppError("Тип объекта не найден.", code="not_found", status_code=404)
    param = db.scalar(
        select(Parameter).where(
            Parameter.object_type_id == object_type.id, Parameter.code == code
        )
    )
    if param is None:
        raise AppError("Параметр не найден.", code="not_found", status_code=404)

    data = payload.model_dump(exclude_unset=True)
    before = {"name": param.name, "default": param.default}
    if "default" in data:
        default_value, default_text = _split_default(param.value_type, data.pop("default"))
        param.default_value = default_value
        param.default_text = default_text
    for field, value in data.items():
        setattr(param, field, value)
    _audit(
        db, user, "update", "parameter", code,
        before=before, after={"name": param.name, "default": param.default},
    )
    db.commit()
    db.refresh(param)
    return _param_out(param)


@router.delete(
    "/object-types/{object_type_code}/parameters/{code}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_parameter(
    object_type_code: str, code: str, db: DbSession, user: AdminUser
) -> None:
    object_type = db.scalar(select(ObjectType).where(ObjectType.code == object_type_code))
    param = (
        db.scalar(
            select(Parameter).where(
                Parameter.object_type_id == object_type.id, Parameter.code == code
            )
        )
        if object_type
        else None
    )
    if param is None:
        raise AppError("Параметр не найден.", code="not_found", status_code=404)
    # Код параметра участвует в расчёте и в требованиях к решениям: удаление
    # сделает существующие проекты непроверяемыми. Поэтому удаление параметра,
    # на который ссылаются проекты, запрещено.
    used = db.scalar(
        select(func.count())
        .select_from(Project)
        .where(Project.object_type_id == object_type.id)
    ) or 0
    if used:
        raise AppError(
            f"Параметр нельзя удалить: он входит в расчёт {used} проект(ов).",
            code="in_use",
            hint="Отключите его или оставьте — на результаты прошлых расчётов "
            "это не влияет.",
        )
    _audit(db, user, "delete", "parameter", code)
    db.delete(param)
    db.commit()


# ── Пользователи ───────────────────────────────────────────────────────────


@router.get("/users", response_model=list[UserAdminOut])
def list_users(
    db: DbSession,
    user: AdminUser,
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict[str, Any]]:
    stmt = (
        select(User, func.count(func.distinct(Project.id)), func.count(func.distinct(Calculation.id)))
        .outerjoin(Project, Project.user_id == User.id)
        .outerjoin(Calculation, Calculation.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )
    if search:
        stmt = stmt.where(User.email.ilike(f"%{search.strip()}%"))
    rows = db.execute(stmt.limit(limit)).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "organization": u.organization,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "last_login_at": u.last_login_at,
            "project_count": pc,
            "calculation_count": cc,
        }
        for u, pc, cc in rows
    ]


@router.patch("/users/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int, payload: UserUpdateAdmin, db: DbSession, user: AdminUser
) -> dict[str, Any]:
    target = db.get(User, user_id)
    if target is None:
        raise AppError("Пользователь не найден.", code="not_found", status_code=404)
    if target.id == user.id and payload.is_active is False:
        raise AppError(
            "Нельзя отключить собственную учётную запись.",
            code="self_disable",
        )
    if target.id == user.id and payload.role is not None and payload.role != "admin":
        raise AppError(
            "Нельзя снять с себя роль администратора.",
            code="self_demote",
            hint="Сначала назначьте администратора другому пользователю.",
        )
    before = {"role": target.role, "is_active": target.is_active}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(target, field, value)
    _audit(db, user, "update", "user", str(target.id), before=before)
    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "email": target.email,
        "full_name": target.full_name,
        "organization": target.organization,
        "role": target.role,
        "is_active": target.is_active,
        "created_at": target.created_at,
        "last_login_at": target.last_login_at,
        "project_count": 0,
        "calculation_count": 0,
    }


# ── Данные ─────────────────────────────────────────────────────────────────


@router.get("/stats")
def platform_stats(db: DbSession, user: AdminUser) -> dict[str, Any]:
    def count(model: Any) -> int:
        return db.scalar(select(func.count()).select_from(model)) or 0

    return {
        "users": count(User),
        "active_users": db.scalar(
            select(func.count()).select_from(User).where(User.is_active.is_(True))
        )
        or 0,
        "projects": count(Project),
        "calculations": count(Calculation),
        "solutions": count(Solution),
        "normatives": count(Normative),
        "object_types": count(ObjectType),
        "with_payback": db.scalar(
            select(func.count())
            .select_from(Calculation)
            .where(Calculation.payback_years.isnot(None))
        )
        or 0,
    }


@router.post("/seed", response_model=SeedRunOut)
def run_seed(
    db: DbSession,
    user: AdminUser,
    force: bool = Query(default=False, description="Перезаписать нормативы и каталог"),
) -> SeedRunOut:
    """Переимпорт данных организатора.

    Идемпотентен: повторный запуск без `force` ничего не меняет, если данные
    уже загружены. На Render база живёт около месяца, поэтому импорт должен
    уметь восстановить себя сам.
    """
    from app.seed.seed import run_seed as _run

    started = time.perf_counter()
    result = _run(db, force=force)
    _audit(db, user, "seed", "database", None, after={"force": force})
    db.commit()
    return SeedRunOut(
        ok=True,
        forced=force,
        duration_ms=int((time.perf_counter() - started) * 1000),
        summary=result.get("summary", result),
        warnings=result.get("warnings", []),
    )


@router.get("/audit")
def audit_log(
    db: DbSession,
    user: AdminUser,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "action": r.action,
            "entity": r.entity,
            "entity_id": r.entity_id,
            "before": r.before,
            "after": r.after,
            "created_at": r.created_at,
        }
        for r in rows
    ]
