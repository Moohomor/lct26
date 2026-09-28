#!/usr/bin/env python
"""Импорт датасета организатора (Датасеты_хакатон.xlsx) и сверка с базой.

Файл датасета уже лежит в репозитории (app/seed/data) и подхватывается при
первом старте приложения. Этот скрипт нужен для двух вещей, которых нет у
автоматического импорта:

  * показать, что именно лежит в книге, — чтобы понимать, откуда взялись
    138 параметров, а не гадать;
  * сверить книгу с базой (`--check`) и упасть с кодом 1, если они разошлись.
    Это то, что стоит запускать в CI после правки датасета.

Запуск (из src/app/services/backend):

    python -m scripts.import_dataset            # отчёт по книге
    python -m scripts.import_dataset --check    # сверка книги с базой
    python -m scripts.import_dataset --import   # переимпортировать в базу
    python -m scripts.import_dataset --import --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import openpyxl
from sqlalchemy import func, select

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import ObjectType, Parameter, ParameterGroup
from app.services.importers.object_params import (
    DATASET_SOURCE,
    SHEET_MAP,
    import_object_parameters,
)
from app.seed.seed import CATASET_FILE

HEADER_ROW = 2  # первая строка — заголовок листа, данные начинаются с третьей


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_workbook(path: Path) -> dict[str, list[tuple[str, str, object]]]:
    """Разбирает книгу в {имя листа: [(параметр, единица, базовое значение)]}.

    Возвращает только те строки, которые импортер действительно возьмёт:
    строку-разделитель секции («▌ …») в список параметров не попадает.
    """
    workbook = openpyxl.load_workbook(path, data_only=True)
    sheets: dict[str, list[tuple[str, str, object]]] = {}

    for sheet_name in SHEET_MAP:
        if sheet_name not in workbook.sheetnames:
            sheets[sheet_name] = []
            continue
        rows: list[tuple[str, str, object]] = []
        for raw in workbook[sheet_name].iter_rows(
            min_row=HEADER_ROW + 1, values_only=True
        ):
            name = _clean(raw[0])
            if not name or name.startswith("▌"):
                continue
            rows.append((name, _clean(raw[1]), raw[2]))
        sheets[sheet_name] = rows
    return sheets


def report(path: Path) -> dict[str, int]:
    """Печатает содержимое книги и возвращает счётчики по листам."""
    if not path.exists():
        print(f"Файл не найден: {path}")
        print(f"Ожидается: {settings.seed_data_dir / CATASET_FILE}")
        raise SystemExit(2)

    workbook = openpyxl.load_workbook(path, data_only=True)
    print(f"Файл      : {path.name} ({path.stat().st_size / 1024:.1f} КБ)")
    print(f"Листов    : {len(workbook.sheetnames)} — {', '.join(workbook.sheetnames)}")

    sheets = read_workbook(path)
    counts: dict[str, int] = {}
    print(f"\n{'Лист':<16}{'код объекта':<14}{'параметров':>12}")
    print("-" * 42)
    for sheet_name, (code, _, _) in SHEET_MAP.items():
        rows = sheets[sheet_name]
        counts[sheet_name] = len(rows)
        print(f"{sheet_name:<16}{code:<14}{len(rows):>12}")

    total = sum(counts.values())
    ignored = set(workbook.sheetnames) - set(SHEET_MAP)
    print(f"\nВсего параметров: {total}")
    if ignored:
        # Легенда — это документация, а не данные: её пропуск ожидаем.
        print(f"Не импортируются: {', '.join(sorted(ignored))} (документация)")
    print(f"Источник данных  : {DATASET_SOURCE}")
    return counts


def check(path: Path) -> int:
    """Сверяет книгу с базой. Возвращает код выхода: 0 — совпадает."""
    from app.models import DataSource

    db = SessionLocal()
    try:
        sheets = read_workbook(path)
        problems: list[str] = []

        for sheet_name, (code, _, _) in SHEET_MAP.items():
            object_type = db.scalar(select(ObjectType).where(ObjectType.code == code))
            if object_type is None:
                problems.append(f"в базе нет типа объекта «{code}» ({sheet_name})")
                continue

            in_file = {name for name, _, _ in sheets[sheet_name]}
            in_db = {p.name for p in object_type.parameters}
            missing = in_file - in_db
            extra = in_db - in_file
            if missing:
                problems.append(
                    f"{code}: в книге есть, в базе нет — {', '.join(sorted(missing)[:5])}"
                    + (" …" if len(missing) > 5 else "")
                )
            if extra:
                problems.append(
                    f"{code}: в базе есть, в книге нет — {', '.join(sorted(extra)[:5])}"
                    + (" …" if len(extra) > 5 else "")
                )
            print(
                f"{code:<12} в книге {len(in_file):>4}   в базе {len(in_db):>4}"
                f"   групп {len(object_type.groups):>3}"
            )

        source = db.scalar(select(DataSource).where(DataSource.name == DATASET_SOURCE))
        if source is None:
            problems.append(f"нет записи об источнике «{DATASET_SOURCE}»")

        totals = {
            "object_types": db.scalar(select(func.count()).select_from(ObjectType)) or 0,
            "parameters": db.scalar(select(func.count()).select_from(Parameter)) or 0,
            "groups": db.scalar(select(func.count()).select_from(ParameterGroup)) or 0,
        }
        print(
            f"\nВсего в базе: типов объектов {totals['object_types']}, "
            f"параметров {totals['parameters']}, групп {totals['groups']}"
        )
    finally:
        db.close()

    if problems:
        print("\nРасхождения (запустите с --import):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nДатасет в базе соответствует книге.")
    return 0


def run_import(path: Path, force: bool) -> int:
    """Переимпортирует книгу. Повторный запуск не плодит дубликаты."""
    db = SessionLocal()
    try:
        result = import_object_parameters(db, path)
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"Импорт не удался: {exc}")
        return 2
    finally:
        db.close()

    print("Импорт завершён:")
    for key, value in result.as_dict().items():
        if key in ("unresolved", "warnings"):
            continue
        print(f"  {key:<14} {value}")
    for item in (*result.unresolved, *result.warnings):
        print(f"  ! {item}")
    if force:
        print("\n--force принят: существующие значения перезаписаны.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--file",
        type=Path,
        default=settings.seed_data_dir / CATASET_FILE,
        help="путь к книге (по умолчанию — датасет в app/seed/data)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="сверить книгу с базой")
    # dest задаётся явно: `import` — зарезервированное слово, `args.import`
    # не разбирается.
    mode.add_argument(
        "--import", dest="do_import", action="store_true", help="загрузить книгу в базу"
    )
    mode.add_argument("--force", action="store_true", help="перезаписать значения")
    args = parser.parse_args(argv)

    path: Path = args.file
    report(path)

    if args.do_import or args.force:
        return run_import(path, force=args.force)
    if args.check:
        return check(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
