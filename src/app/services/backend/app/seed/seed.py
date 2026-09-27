"""Загрузка стартовых данных платформы.

Порядок важен: справочники типов объектов должны появиться до параметров,
параметры — до проектов, а нормативы — до любого расчёта.

Функция идемпотентна и безопасна для повторного запуска. Это не удобство,
а необходимость: бесплатная база Render удаляется примерно через 30 дней,
и приложение должно восстанавливать данные само при каждом старте.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import (
    CatalogVersion,
    DataSource,
    ImportBatch,
    Normative,
    ObjectType,
    Parameter,
    Process,
    Solution,
    SolutionType,
    User,
    Vendor,
)
from app.models.project import Project, Scenario
from app.seed.normatives_seed import NORMATIVES
from app.services.importers.catalog_csv import import_catalog
from app.services.importers.catalog_taxonomy import PROCESSES
from app.services.importers.object_params import import_object_parameters
from app.services.importers.reference_solutions import import_reference_solutions

logger = logging.getLogger(__name__)

CATASET_FILE = "Датасеты_хакатон.xlsx"
CATALOG_FILE = "catalog_export_v4.csv"

# Версия каталога попадает в каждый расчёт (ТЗ 3.1.5): по ней видно,
# на каких данных получен результат.
CATALOG_VERSION = "catalog-v4+ref-1.0"
PARAMS_VERSION = "params-organizer-1.0"

DEMO_ADMIN_EMAIL = "admin@demo.local"
DEMO_USER_EMAIL = "user@demo.local"
DEMO_PASSWORD = "demo12345"


@dataclass
class SeedReport:
    object_types: int = 0
    parameters: int = 0
    groups: int = 0
    processes: int = 0
    solution_types: int = 0
    solutions: int = 0
    catalog_applicable: int = 0
    verified_solutions: int = 0
    normatives: int = 0
    vendors: int = 0
    demo_users: int = 0
    batches: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    skipped_reason: str | None = None

    def as_dict(self) -> dict:
        return {
            "object_types": self.object_types,
            "parameters": self.parameters,
            "groups": self.groups,
            "processes": self.processes,
            "solution_types": self.solution_types,
            "solutions": self.solutions,
            "catalog_applicable": self.catalog_applicable,
            "verified_solutions": self.verified_solutions,
            "normatives": self.normatives,
            "vendors": self.vendors,
            "demo_users": self.demo_users,
            "batches": self.batches,
            "warnings": self.warnings,
            "skipped_reason": self.skipped_reason,
        }


def _data_dir() -> Path:
    return settings.seed_data_dir


def _upsert_normatives(db: Session) -> int:
    existing = {n.code: n for n in db.scalars(select(Normative))}
    count = 0
    for defn in NORMATIVES:
        row = existing.get(defn.code)
        if row is None:
            db.add(
                Normative(
                    code=defn.code,
                    name=defn.name,
                    value=defn.value,
                    unit=defn.unit,
                    category=defn.category,
                    source=defn.source,
                    note=defn.note,
                    model_version=settings.calc_model_version,
                    is_editable=defn.is_editable,
                )
            )
        else:
            row.name = defn.name
            row.value = defn.value
            row.unit = defn.unit
            row.category = defn.category
            row.source = defn.source
            row.note = defn.note
            row.is_editable = defn.is_editable
        count += 1
    db.flush()
    return count


def _upsert_processes(db: Session) -> int:
    object_types = {ot.code: ot for ot in db.scalars(select(ObjectType))}
    existing = {(p.object_type.code if p.object_type else None, p.code): p for p in db.scalars(select(Process))}
    count = 0
    for order, defn in enumerate(PROCESSES):
        object_type = object_types.get(defn.object_type)
        if object_type is None:
            logger.warning("Тип объекта %s не найден — процесс %s пропущен", defn.object_type, defn.code)
            continue
        key = (defn.object_type, defn.code)
        row = existing.get(key)
        if row is None:
            db.add(
                Process(
                    object_type_id=object_type.id,
                    code=defn.code,
                    name=defn.name,
                    description=defn.description,
                    metric_code=defn.metric_code,
                    order_index=order,
                )
            )
        else:
            row.name = defn.name
            row.description = defn.description
            row.metric_code = defn.metric_code
            row.object_type_id = object_type.id
            row.order_index = order
        count += 1
    db.flush()
    return count


def _refresh_catalog_version(db: Session, note: str, batch_id) -> str:
    row = db.scalar(select(CatalogVersion).where(CatalogVersion.version == CATALOG_VERSION))
    solutions_count = db.scalar(select(func.count()).select_from(Solution)) or 0
    if row is None:
        row = CatalogVersion(
            version=CATALOG_VERSION,
            solutions_count=solutions_count,
            is_current=True,
            import_batch_id=batch_id,
            note=note,
        )
        db.add(row)
    else:
        row.solutions_count = solutions_count
        row.is_current = True
        row.note = note
    db.execute(
        CatalogVersion.__table__.update()
        .where(CatalogVersion.version != CATALOG_VERSION)
        .values(is_current=False)
    )
    db.flush()
    return CATALOG_VERSION


def _ensure_demo_users(db: Session) -> int:
    from app.core.security import hash_password

    created = 0
    specs = (
        (DEMO_ADMIN_EMAIL, "Администратор платформы", "admin"),
        (DEMO_USER_EMAIL, "Пользователь платформы", "user"),
    )
    for email, full_name, role in specs:
        existing = db.scalar(select(User).where(User.email == email))
        if existing is None:
            db.add(
                User(
                    email=email,
                    password_hash=hash_password(DEMO_PASSWORD),
                    full_name=full_name,
                    role=role,
                    organization="Демонстрационный аккаунт",
                    is_active=True,
                )
            )
            created += 1
    db.flush()
    return created


def _already_seeded(db: Session) -> bool:
    """Быстрая проверка: данные организатора уже загружены."""
    return bool(
        db.scalar(select(func.count()).select_from(Normative).where(Normative.code == "calc.horizon_years"))
    ) and bool(db.scalar(select(func.count()).select_from(ObjectType)))


def run_seed(db: Session, *, force: bool = False) -> SeedReport:
    report = SeedReport()
    data_dir = _data_dir()

    if not force and _already_seeded(db):
        report.skipped_reason = "Данные уже загружены (используйте force=True для перезагрузки)."
        report.normatives = db.scalar(select(func.count()).select_from(Normative)) or 0
        report.solutions = db.scalar(select(func.count()).select_from(Solution)) or 0
        report.object_types = db.scalar(select(func.count()).select_from(ObjectType)) or 0
        report.parameters = db.scalar(select(func.count()).select_from(Parameter)) or 0
        return report

    # 1. Нормативы расчётной модели — нужны всему остальному.
    report.normatives = _upsert_normatives(db)

    # 2. Типы объектов и их параметры из демо-датасета.
    dataset_path = data_dir / CATASET_FILE
    if dataset_path.exists():
        params_result = import_object_parameters(db, dataset_path)
        report.object_types = params_result.object_types
        report.parameters = params_result.parameters
        report.groups = params_result.groups
        report.warnings.extend(params_result.unresolved)
        report.batches.append({"kind": "object_params", **params_result.as_dict()})
    else:
        report.warnings.append(f"Файл {CATASET_FILE} не найден в {data_dir}")

    # 3. Процессы объектов (иерархия ТЗ 3.3.1).
    report.processes = _upsert_processes(db)

    # 4. Каталог решений из выгрузки организатора.
    catalog_path = data_dir / CATALOG_FILE
    if catalog_path.exists():
        catalog_result = import_catalog(db, catalog_path)
        report.solutions = catalog_result.created
        report.catalog_applicable = catalog_result.applicable
        report.vendors = catalog_result.vendors
        report.warnings.extend(catalog_result.warnings)
        report.batches.append({"kind": "catalog_csv", **catalog_result.as_dict()})
    else:
        report.warnings.append(f"Файл {CATALOG_FILE} не найден в {data_dir}")

    # 5. Эталонные решения с подтверждёнными ТТХ.
    ref_result = import_reference_solutions(db)
    report.verified_solutions = db.scalar(
        select(func.count()).select_from(Solution).where(Solution.is_verified.is_(True))
    ) or 0
    report.solution_types = db.scalar(select(func.count()).select_from(SolutionType)) or 0
    report.batches.append({"kind": "reference_solutions", **ref_result.as_dict()})
    report.warnings.extend(ref_result.warnings)

    # 6. Версия каталога и журнал импорта.
    for batch_payload in report.batches:
        db.add(
            ImportBatch(
                kind=batch_payload.get("kind", "unknown"),
                source_file=CATALOG_FILE if batch_payload.get("kind") == "catalog_csv" else CATASET_FILE,
                status="done",
                created_count=batch_payload.get("created", 0)
                or batch_payload.get("object_types", 0),
                updated_count=batch_payload.get("updated", 0),
                skipped_count=batch_payload.get("skipped_no_name", 0),
                warnings=[w for w in (batch_payload.get("warnings") or [])][:50] or None,
                notes=f"Загружено {date.today().isoformat()}",
            )
        )
    db.flush()
    latest_batch = db.scalar(select(ImportBatch).order_by(ImportBatch.created_at.desc()).limit(1))
    _refresh_catalog_version(db, "Загрузка данных организатора при старте", latest_batch.id if latest_batch else None)

    # 7. Демонстрационные аккаунты — чтобы платформой можно было пользоваться
    #    сразу после развёртывания, без ручной регистрации администратора.
    report.demo_users = _ensure_demo_users(db)

    db.commit()
    return report


def seed_summary(db: Session) -> dict:
    """Краткая сводка о состоянии данных — показывается в /health и в админке."""
    return {
        "object_types": db.scalar(select(func.count()).select_from(ObjectType)) or 0,
        "parameters": db.scalar(select(func.count()).select_from(Parameter)) or 0,
        "processes": db.scalar(select(func.count()).select_from(Process)) or 0,
        "solution_types": db.scalar(select(func.count()).select_from(SolutionType)) or 0,
        "vendors": db.scalar(select(func.count()).select_from(Vendor)) or 0,
        "solutions": db.scalar(select(func.count()).select_from(Solution)) or 0,
        "verified_solutions": db.scalar(
            select(func.count()).select_from(Solution).where(Solution.is_verified.is_(True))
        )
        or 0,
        "normatives": db.scalar(select(func.count()).select_from(Normative)) or 0,
        "data_sources": db.scalar(select(func.count()).select_from(DataSource)) or 0,
        "users": db.scalar(select(func.count()).select_from(User)) or 0,
        "projects": db.scalar(select(func.count()).select_from(Project)) or 0,
        "scenarios": db.scalar(select(func.count()).select_from(Scenario)) or 0,
    }
