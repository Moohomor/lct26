"""Наложение ТТХ из документа организатора на позиции каталога.

Импорт каталога даёт название, поставщика и цену, но не технические
характеристики. Этот модуль дописывает ТТХ восьми эталонным изделиям,
связывая их с уже загруженными позициями по названию, и создаёт
отсутствующие (шаттл Stelcon, тягач Cognitive Pilot, PuduBot 2).

Связывание идёт по slug, заданному в reference_solutions_seed, — он же
записывается в `raw.slug`, поэтому повторный запуск обновляет те же строки
и не плодит дубликаты.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DataSource, Solution, SolutionType, Vendor
from app.services.importers.catalog_csv import compute_completeness
from app.seed.reference_solutions_seed import (
    PRICE_ESTIMATES,
    REFERENCE_SOLUTIONS,
    ReferenceSolution,
)

SLUG_KEY = "slug"


@dataclass
class ReferenceImportResult:
    created: int = 0
    linked_to_catalog: int = 0
    estimated_price: int = 0
    unmatched_catalog: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "created": self.created,
            "linked_to_catalog": self.linked_to_catalog,
            "estimated_price": self.estimated_price,
            "unmatched_catalog": self.unmatched_catalog,
            "warnings": self.warnings,
        }


def _source_for(ref: ReferenceSolution, db: Session) -> DataSource:
    source = db.scalar(select(DataSource).where(DataSource.name == ref.source_name))
    if source is None:
        source = DataSource(
            name=ref.source_name,
            url=ref.source_url,
            kind="vendor_site",
            is_verified=True,
            note=(
                "ТТХ приведены организатором как пример решения по каждому типу "
                "роботизации. Значения уточняются по ссылке производителя."
            ),
        )
        db.add(source)
        db.flush()
    return source


def _vendor(name: str, db: Session) -> Vendor:
    vendor = db.scalar(select(Vendor).where(Vendor.name == name))
    if vendor is None:
        vendor = Vendor(name=name)
        db.add(vendor)
        db.flush()
    return vendor


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    return text.lower().replace("ё", "е").replace("«", "").replace("»", "").strip()


def _find_by_slug(db: Session, slug: str) -> Solution | None:
    solutions = db.scalars(select(Solution)).all()
    for sol in solutions:
        if (sol.raw or {}).get(SLUG_KEY) == slug:
            return sol
    return None


def _find_in_catalog(db: Session, ref: ReferenceSolution) -> Solution | None:
    """Ищет уже загруженную позицию каталога по названию продукта."""
    if not ref.catalog_match:
        return None
    needle = _normalize(ref.catalog_match)
    best: Solution | None = None
    for sol in db.scalars(select(Solution)):
        if sol.is_variant_of_id is not None:
            continue
        haystack = _normalize(sol.name)
        if needle in haystack or haystack in needle:
            # при нескольких совпадениях берём самую короткую строку:
            # «Ronavi H1500» короче, чем «Ronavi H1500 (грузоподъемность …)»
            if best is None or len(sol.name) < len(best.name):
                best = sol
    return best


def import_reference_solutions(db: Session) -> ReferenceImportResult:
    result = ReferenceImportResult()
    type_by_code = {st.code: st for st in db.scalars(select(SolutionType))}

    for ref in REFERENCE_SOLUTIONS:
        if ref.solution_type not in type_by_code:
            result.warnings.append(
                f"Тип решения «{ref.solution_type}» отсутствует в справочнике — "
                f"позиция {ref.name} пропущена."
            )
            continue

        source = _source_for(ref, db)
        vendor = _vendor(ref.vendor, db)
        solution_type = type_by_code[ref.solution_type]

        solution = _find_by_slug(db, ref.slug) or _find_in_catalog(db, ref)
        was_already_marked = solution is not None and (solution.raw or {}).get(SLUG_KEY) == ref.slug

        if solution is None:
            solution = Solution(
                name=ref.name,
                solution_type_id=solution_type.id,
                status="operation",
                is_verified=True,
                raw={SLUG_KEY: ref.slug, "source": "organizer_reference_doc"},
            )
            db.add(solution)
            db.flush()
            result.created += 1
        elif not was_already_marked:
            # Позиция каталога получила ТТХ: в карточке решения теперь видно
            # и происхождение из выгрузки организатора, и источник ТТХ.
            result.linked_to_catalog += 1

        solution.vendor_id = vendor.id
        solution.solution_type_id = solution_type.id
        solution.name = ref.name
        solution.applicable_object_types = list(ref.object_types)
        solution.process_codes = list(ref.process_codes)
        solution.data_source_id = source.id
        solution.is_verified = True
        if ref.note:
            solution.description = ref.note
        if ref.restrictions:
            solution.restrictions = list(ref.restrictions)
        solution.infrastructure_requirements = (
            solution.infrastructure_requirements
            or "Требуется ровное половое покрытие и зона разворота; "
            "зарядная станция в радиусе досягаемости."
        )

        for field_name, value in ref.specs.items():
            setattr(solution, field_name, value)

        # Цена: из каталога организатора, иначе — явное оценочное допущение.
        if solution.price_source != "catalog":
            estimate = PRICE_ESTIMATES.get(ref.slug)
            if estimate is not None:
                solution.unit_price_rub = estimate
                solution.price_source = "estimate"
                result.estimated_price += 1

        raw = dict(solution.raw or {})
        raw[SLUG_KEY] = ref.slug
        raw["source"] = "organizer_reference_doc"
        raw["specs_source"] = ref.source_url
        solution.raw = raw
        # Полнота данных считается после наложения ТТХ, иначе позиция,
        # обогащённая характеристиками, продолжала бы выглядеть пустой.
        solution.completeness = compute_completeness(solution)

    db.flush()

    # Позиции каталога, для которых не нашлось эталона, оставляем как есть:
    # «данные не подтверждены» — это допустимое состояние по ТЗ 3.3.4.
    known = {r.slug for r in REFERENCE_SOLUTIONS}
    for sol in db.scalars(select(Solution)):
        if sol.is_variant_of_id is not None:
            continue
        if (sol.raw or {}).get(SLUG_KEY) in known:
            continue
        if sol.is_verified:
            continue
        if sol.raw and sol.raw.get("source") == "organizer_reference_doc":
            result.unmatched_catalog.append(sol.name)

    return result
