"""Импорт каталога решений (CSV организатора) в таблицу `solutions`.

Особенности файла, на которые здесь есть ответы:

* 223 строки, но лишь 187 уникальных `id` — повторы по Дополнениям (п. 6)
  трактуются как комплектации одного решения: первая строка становится
  основной позицией, остальные — её варианты (`is_variant_of_id`);
* цены приходят в русском формате «2 700 000,00» и включают НДС;
* технические характеристики в файле отсутствуют, поэтому `completeness`
  для большинства позиций низкий, и подбор помечает их как требующие
  уточнения данных у поставщика, а не выдаёт за подтверждённые ТТХ.
"""

from __future__ import annotations

import csv
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DataSource, Solution, SolutionType, Vendor
from app.services.importers.catalog_taxonomy import (
    SOLUTION_TYPES,
    detect_processes,
    detect_solution_type,
)
from app.services.importers.normalize import clean_text, dedupe, parse_number

CATALOG_SOURCE_NAME = "Каталог решений организатора (catalog_export_v4.csv)"

# Поля ТТХ, по которым считается полнота данных позиции (ТЗ 3.3.4).
COMPLETENESS_FIELDS = (
    "payload_kg",
    "throughput_per_hour",
    "unit_price_rub",
    "autonomy_hours",
    "max_speed_mps",
    "min_temp_c",
    "max_temp_c",
    "navigation_types",
    "lifetime_years",
    "service_rate_pct",
)

# Отрасли файла организатора, не относящиеся к трём базовым объектам.
# Позиции сохраняются в каталоге, но помечаются как неприменимые.
IRRELEVANT_INDUSTRIES = {"Лесное хозяйство", "Сельское хозяйство", "ТЭК"}


@dataclass
class CatalogImportResult:
    total_rows: int = 0
    created: int = 0
    updated: int = 0
    variants: int = 0
    skipped_no_name: int = 0
    vendors: int = 0
    solution_types: int = 0
    applicable: int = 0
    not_applicable: int = 0
    no_price: int = 0
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "total_rows": self.total_rows,
            "created": self.created,
            "updated": self.updated,
            "variants": self.variants,
            "skipped_no_name": self.skipped_no_name,
            "vendors": self.vendors,
            "solution_types": self.solution_types,
            "applicable": self.applicable,
            "not_applicable": self.not_applicable,
            "no_price": self.no_price,
            "warnings": self.warnings,
        }


def _get_or_create_source(db: Session) -> DataSource:
    source = db.scalar(select(DataSource).where(DataSource.name == CATALOG_SOURCE_NAME))
    if source is None:
        source = DataSource(
            name=CATALOG_SOURCE_NAME,
            kind="organizer",
            is_verified=True,
            note=(
                "Выгрузка каталога решений, предоставленная организатором. "
                "Цены указаны с НДС; технические характеристики приведены "
                "только в примерах решений (см. batch reference_solutions)."
            ),
        )
        db.add(source)
        db.flush()
    return source


def _sync_taxonomy(db: Session) -> dict[str, SolutionType]:
    """Создаёт/обновляет справочник типов решений. Возвращает код → запись."""
    by_code: dict[str, SolutionType] = {st.code: st for st in db.scalars(select(SolutionType))}
    for order, st in enumerate(SOLUTION_TYPES):
        existing = by_code.get(st.code)
        if existing is None:
            existing = SolutionType(
                code=st.code,
                name=st.name,
                description=st.description,
                is_mobile=st.is_mobile,
                requires_passage=st.requires_passage,
                passage_margin_m=Decimal(str(st.passage_margin_m)),
                order_index=order,
            )
            db.add(existing)
        else:
            existing.name = st.name
            existing.description = st.description
            existing.is_mobile = st.is_mobile
            existing.requires_passage = st.requires_passage
            existing.passage_margin_m = Decimal(str(st.passage_margin_m))
            existing.order_index = order
        by_code[st.code] = existing
    db.flush()
    return by_code


def compute_completeness(solution: Solution) -> Decimal:
    """Доля заполненных ключевых ТТХ, % (ТЗ 3.3.4: степень полноты данных)."""
    filled = sum(1 for f in COMPLETENESS_FIELDS if getattr(solution, f) is not None)
    return Decimal(str(round(100 * filled / len(COMPLETENESS_FIELDS), 2)))


def _read_rows(path: Path) -> list[dict[str, str]]:
    # utf-8-sig: файл организатора сохранён с BOM, иначе первая колонка
    # называется «﻿id» и id перестаёт читаться.
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def import_catalog(db: Session, path: Path) -> CatalogImportResult:
    result = CatalogImportResult()
    source = _get_or_create_source(db)
    solution_types = _sync_taxonomy(db)
    result.solution_types = len(solution_types)

    rows = _read_rows(path)
    result.total_rows = len(rows)

    vendors: dict[str, Vendor] = {v.name: v for v in db.scalars(select(Vendor))}

    # Ключ идемпотентности — номер строки исходного CSV. Он стабилен между
    # запусками, поэтому повторная загрузка обновляет те же записи, а варианты
    # одного catalog_id не плодятся заново.
    existing_solutions = list(db.scalars(select(Solution)))
    by_csv_row: dict[int, Solution] = {
        (sol.raw or {}).get("csv_row"): sol
        for sol in existing_solutions
        if (sol.raw or {}).get("csv_row")
    }
    # Основная позиция для каждого catalog_id (первая строка с этим id).
    primary_by_catalog_id: dict[uuid.UUID, Solution] = {}
    for sol in existing_solutions:
        if sol.catalog_id is not None and sol.is_variant_of_id is None:
            primary_by_catalog_id.setdefault(sol.catalog_id, sol)

    # Сколько строк приходится на каждый catalog_id — нужно, чтобы отметить
    # варианты, а не плодить копии одной и той же позиции.
    id_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        raw_id = (row.get("id") or "").strip()
        if raw_id:
            id_counts[raw_id] += 1

    claimed_catalog_ids: dict[uuid.UUID, int] = {}

    for row_index, row in enumerate(rows):
        name = clean_text(row.get("Название"))
        if not name:
            result.skipped_no_name += 1
            continue

        raw_id = (row.get("id") or "").strip()
        catalog_id: uuid.UUID | None = None
        if raw_id:
            try:
                catalog_id = uuid.UUID(raw_id)
            except ValueError:
                result.warnings.append(
                    f"Строка {row_index + 2}: id «{raw_id}» не является UUID, "
                    "позиция сохранена без внешнего идентификатора."
                )

        subtype = clean_text(row.get("Подтип"))
        type_label = clean_text(row.get("Тип"))
        scenario = clean_text(row.get("Сценарий"))
        industry = clean_text(row.get("Отрасль"))
        company = clean_text(row.get("компания"))

        st_code = detect_solution_type(subtype, type_label, name)
        processes = detect_processes(scenario, subtype)

        # Применимость: только по процессам базовых объектов. Отрасль «ТЭК» или
        # «Сельское хозяйство» означает, что позиция в складскую/аэропортную/
        # медицинскую логистику не попадает даже при совпадении слова «логистика».
        if industry in IRRELEVANT_INDUSTRIES:
            processes = []

        object_types = dedupe([ot for ot, _pc in processes])
        process_codes = dedupe(
            [pc for ot, pc in processes if ot in object_types]
        )
        applicable = bool(object_types)

        # ── Производитель ──────────────────────────────────────────────────
        vendor = None
        if company:
            vendor = vendors.get(company)
            if vendor is None:
                vendor = Vendor(name=company)
                db.add(vendor)
                db.flush()
                vendors[company] = vendor
                result.vendors += 1

        price = parse_number(row.get("Цена изделия"))
        if price is None:
            result.no_price += 1

        csv_row = row_index + 2
        payload: dict[str, object] = {
            "vendor_id": vendor.id if vendor else None,
            "solution_type_id": solution_types[st_code].id if st_code in solution_types else None,
            "name": name,
            "catalog_id": catalog_id,
            "status": (clean_text(row.get("статус")) or "operation"),
            "purpose": scenario,
            "description": clean_text(row.get("описание")),
            "industry": industry,
            "region": clean_text(row.get("Регион")),
            "scenario_label": scenario,
            "cases": clean_text(row.get("Кейсы")),
            "trl": _int_or_none(row.get("УГТ")),
            "market_potential": parse_number(row.get("Рын Потенциал")),
            "unit_price_rub": price,
            "price_source": "catalog" if price is not None else None,
            "applicable_object_types": object_types or None,
            "process_codes": process_codes or None,
            "data_source_id": source.id,
            "is_verified": False,
            "raw": {
                "csv_row": csv_row,
                "type_label": type_label,
                "subtype": subtype,
                "solution_type_detected": st_code,
                "detected_processes": [
                    {"object_type": ot, "process": pc} for ot, pc in processes
                ],
            },
        }

        existing = by_csv_row.get(csv_row)

        # Повтор по catalog_id внутри одной выгрузки — это комплектация того же
        # решения (Дополнения п. 6): своя строка со ссылкой на основную позицию.
        is_variant = bool(
            catalog_id
            and claimed_catalog_ids.get(catalog_id) is not None
            and claimed_catalog_ids[catalog_id] != csv_row
        )
        if is_variant and id_counts[raw_id] > 1:
            result.variants += 1

        if existing is not None:
            for key, value in payload.items():
                setattr(existing, key, value)
            solution = existing
            result.updated += 1
        else:
            if is_variant:
                primary = primary_by_catalog_id.get(catalog_id)  # type: ignore[arg-type]
                if primary is not None:
                    payload["is_variant_of_id"] = primary.id
                    payload["variant_label"] = f"Комплектация {id_counts[raw_id]}"
            solution = Solution(**payload)  # type: ignore[arg-type]
            db.add(solution)
            db.flush()
            by_csv_row[csv_row] = solution
            if catalog_id is not None and not is_variant:
                primary_by_catalog_id.setdefault(catalog_id, solution)
            result.created += 1

        if catalog_id is not None and claimed_catalog_ids.get(catalog_id) is None:
            claimed_catalog_ids[catalog_id] = csv_row

        solution.completeness = compute_completeness(solution)
        if applicable:
            result.applicable += 1
        else:
            result.not_applicable += 1

    return result


def _int_or_none(value: object) -> int | None:
    num = parse_number(value)
    if num is None:
        return None
    try:
        return int(num)
    except (ValueError, ArithmeticError):
        return None
