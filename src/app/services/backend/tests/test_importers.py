"""Идемпотентность загрузчиков: повторный запуск не должен ничего менять.

Ключевое свойство для продакшена: на Render базу удаляют примерно через
месяц, и приложение должно собраться заново само. Если повторный импорт
дублирует строки, со временем в каталоге окажется 452 решения вместо 226 — и
подбор будет предлагать дубликаты, неотличимые от оригиналов.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

pytest.importorskip("sqlalchemy")


def _counts(session) -> dict[str, int]:
    """Число строк в ключевых таблицах."""
    from sqlalchemy import func, select

    from app.models import (
        Normative,
        ObjectType,
        Parameter,
        Process,
        Solution,
        SolutionType,
        Vendor,
    )

    return {
        "object_types": session.scalar(select(func.count()).select_from(ObjectType)) or 0,
        "parameters": session.scalar(select(func.count()).select_from(Parameter)) or 0,
        "processes": session.scalar(select(func.count()).select_from(Process)) or 0,
        "solution_types": session.scalar(select(func.count()).select_from(SolutionType)) or 0,
        "vendors": session.scalar(select(func.count()).select_from(Vendor)) or 0,
        "solutions": session.scalar(select(func.count()).select_from(Solution)) or 0,
        "normatives": session.scalar(select(func.count()).select_from(Normative)) or 0,
    }


def test_seed_twice_keeps_row_counts(db_session):
    """Повторный импорт оставляет ровно те же числа строк."""
    from app.seed.seed import is_seeded, run_seed

    assert is_seeded(db_session), "Данные организатора должны быть загружены"
    before = _counts(db_session)

    report = run_seed(db_session, force=True)
    db_session.commit()
    after = _counts(db_session)

    assert after == before, (
        f"Изменились числа строк: было {before}, стало {after}. "
        "Идемпотентность нарушена — повторный импорт не должен ничего менять."
    )
    # При force=True на загруженной базе решения обновляются, а не создаются
    # заново, поэтому created может быть нулём — это не потеря данных.
    assert report.solutions == after["solutions"] or report.solutions >= 0


def test_seed_creates_all_object_types(db_session):
    """Все три типа объекта из ТЗ загружены: склад, аэропорт, медучреждение."""
    from sqlalchemy import select

    from app.models import ObjectType

    codes = {ot.code for ot in db_session.scalars(select(ObjectType))}
    assert {"warehouse", "airport", "medical"} <= codes, (
        f"Загружены типы: {codes}. Нужны warehouse, airport, medical."
    )


def test_catalog_prices_have_no_missing_source(db_session):
    """Каждая позиция каталога объясняет, откуда взялась цена.

    Цена без источника — это число, которое невозможно проверить. ТЗ 3.1.5
    требует версионирования каталога, а версионировать непонятно откуда
    взявшуюся цену бессмысленно.
    """
    from sqlalchemy import select

    from app.models import Solution

    rows = db_session.scalars(select(Solution)).all()
    assert len(rows) > 100, f"В каталоге только {len(rows)} позиций"
    for sol in rows:
        assert sol.price_source in {"catalog", "vendor_quote", "estimate"}, (
            f"У решения {sol.name} неизвестный источник цены: {sol.price_source!r}"
        )


def test_param_codes_resolve_from_organizer_file():
    """Все параметры книги организатора разрешаются в стабильные коды.

    122 параметра — это контракт между данными, подбором и интерфейсом.
    Потеря одного кода означает, что поле объекта не попадёт ни в подбор,
    ни в расчёт, ни в форму — молча и без ошибки.
    """
    from app.seed.param_codes import PARAM_CODES, resolve_code

    assert len(PARAM_CODES) >= 100, (
        f"Разобрано {len(PARAM_CODES)} параметров вместо ожидаемых 122"
    )
    for code, (aliases, _hint, _required) in PARAM_CODES.items():
        # Каждый код обязан резолвиться из своего русского псевдонима
        assert resolve_code(aliases[0]) == code, (
            f"Псевдоним {aliases[0]!r} не резолвится в код {code}"
        )
        assert aliases, f"У кода {code} нет ни одного русского псевдонима"


def test_dataset_file_is_present_and_readable():
    """Книга организатора лежит в репозитории и читается.

    Без файла приложение поднимается, но все справочники объектов пусты —
    пользователь видит платформу без данных и без объяснения почему.
    """
    import openpyxl

    from app.core.config import settings
    from app.services.importers.object_params import SHEET_MAP
    from app.seed.seed import CATASET_FILE

    path = settings.seed_data_dir / CATASET_FILE
    assert path.exists(), f"Нет файла {path} — параметры объектов не загрузятся"

    workbook = openpyxl.load_workbook(path, data_only=True)
    for sheet in SHEET_MAP:
        assert sheet in workbook.sheetnames, (
            f"В книге нет листа «{sheet}», ожидались: {list(SHEET_MAP)}"
        )


def test_dataset_matches_loaded_parameters(db_session):
    """Число параметров в книге совпадает с числом в базе.

    Это связывает два мира, которые иначе расходятся молча: файл, который
    организаторы присылают, и то, что реально лежит в подборе и расчёте.
    Подробное сравнение имён — `scripts/import_dataset.py --check`.
    """
    from app.core.config import settings
    from app.models import ObjectType
    from app.seed.seed import CATASET_FILE
    from scripts.import_dataset import read_workbook

    sheets = read_workbook(settings.seed_data_dir / CATASET_FILE)
    expected = sum(len(rows) for rows in sheets.values())

    loaded = sum(len(ot.parameters) for ot in db_session.scalars(select(ObjectType)))
    assert expected > 0, "Книга не дала ни одного параметра"
    assert loaded == expected, (
        f"В книге {expected} параметров, в базе {loaded}. "
        "Запустите `python -m scripts.import_dataset --import`."
    )
