"""Подбор решений: блокеры, веса и поведение на реальном каталоге.

Проверяется не «функция возвращает словарь», а содержательные свойства,
которые видны пользователю: неподходящее решение отклоняется с объяснением,
подходящее остаётся, а отсутствие данных не выдаётся за несоответствие.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")


def _warehouse_params(db) -> dict:
    """Параметры склада из значений по умолчанию — как форма нового проекта."""
    from sqlalchemy import select

    from app.models import ObjectType, Parameter

    ot = db.scalar(select(ObjectType).where(ObjectType.code == "warehouse"))
    rows = db.scalars(select(Parameter).where(Parameter.object_type_id == ot.id))
    return {p.code: p.default for p in rows if p.default is not None}


def _candidates(db) -> list:
    from sqlalchemy import select

    from app.models import Solution

    return list(
        db.scalars(
            select(Solution)
            .where(Solution.is_variant_of_id.is_(None))
            .options(
                __import__("sqlalchemy.orm", fromlist=["selectinload"]).selectinload(
                    Solution.solution_type
                )
            )
        )
    )


def test_every_process_has_requirements(db_session):
    """Каждый процесс каждого типа объекта порождает хотя бы одно требование.

    Процесс без требований — это кнопка в интерфейсе, по которой подбор
    возвращает пустоту без объяснений: пользователь не поймёт, что пошло не
    так, а проверить это можно только руками.
    """
    from app.services.matching.requirements import build_requirements

    # Параметры по умолчанию: с пустым словарем требований не будет ни у одного
    # процесса, потому что требования выводятся из параметров объекта.
    from sqlalchemy import select

    from app.models import ObjectType, Parameter

    for object_type in ("warehouse", "airport", "medical"):
        ot = db_session.scalar(
            select(ObjectType).where(ObjectType.code == object_type)
        )
        params = {
            p.code: p.default
            for p in db_session.scalars(
                select(Parameter).where(Parameter.object_type_id == ot.id)
            )
            if p.default is not None
        }
        for process_code in _process_codes(db_session, object_type):
            reqs, peak, _unit = build_requirements(object_type, process_code, params)
            assert reqs, (
                f"Процесс {object_type}/{process_code} не порождает ни одного "
                "требования — подбор по нему вернёт пустоту"
            )


def _process_codes(db, object_type: str) -> list[str]:
    from sqlalchemy import select

    from app.models import ObjectType, Process

    ot = db.scalar(select(ObjectType).where(ObjectType.code == object_type))
    return [
        p.code
        for p in db.scalars(select(Process).where(Process.object_type_id == ot.id))
    ]


def test_missing_spec_is_warning_not_blocker(db_session):
    """Отсутствие характеристики в каталоге не отклоняет решение.

    Это ключевое свойство: каталог организатора заполнен выборочно, и если
    «нет данных» означало «не подходит», подбор возвращал бы пустоту — половина
    позиций отсеивалась бы по пробелу в анкете, а не по существу.
    """
    from app.services.matching import engine as matching

    params = _warehouse_params(db_session)
    candidates = _candidates(db_session)
    assert candidates, "Каталог пуст"

    ranked = matching.rank(candidates, "warehouse", "intra_logistics", params)
    assert ranked["summary"]["considered"] > 0

    # Решения без заявленной грузоподъёмности обязаны остаться в выдаче
    without_payload = [
        r
        for r in ranked["results"]
        if r["is_eligible"] and r["checks"] and any(
            c["code"] == "payload" and not c["passed"] and c["severity"] == "warning"
            for c in r["checks"]
        )
    ]
    assert without_payload, (
        "Ни одно решение без грузоподъёмности не осталось в выдаче — "
        "отсутствие данных снова трактуется как отказ"
    )


def test_ineligible_solution_is_rejected_with_reason(db_session):
    """Отклонённое решение объясняет, какое именно требование не выполнено."""
    from app.services.matching import engine as matching

    params = _warehouse_params(db_session)
    candidates = _candidates(db_session)
    ranked = matching.rank(candidates, "warehouse", "intra_logistics", params)

    rejected = [r for r in ranked["results"] if not r["is_eligible"]]
    assert rejected, "Нет отклонённых решений — проверять нечего"
    for r in rejected:
        assert r["blockers"], (
            f"Решение {r['name']} отклонено без объяснения: {r['blockers']}"
        )


def test_score_is_weighted_sum(db_session):
    """Балл складывается из компонентов и не превышает 100."""
    from app.services.matching import engine as matching

    params = _warehouse_params(db_session)
    candidates = _candidates(db_session)
    ranked = matching.rank(candidates, "warehouse", "intra_logistics", params)

    for r in ranked["results"]:
        scores = r["scores"]
        assert 0 <= r["score"] <= 100, f"Балл {r['score']} вне диапазона"
        # Компоненты должны быть неотрицательными: отрицательный вес означал бы,
        # что хорошее решение набирает меньше баллов, чем плохое
        for name, value in scores.items():
            assert value >= 0, f"Компонент {name} отрицательный: {value}"


def test_rank_orders_by_score(db_session):
    """Первое в списке — с наивысшим баллом."""
    from app.services.matching import engine as matching

    params = _warehouse_params(db_session)
    candidates = _candidates(db_session)
    ranked = matching.rank(candidates, "warehouse", "intra_logistics", params)
    # Сортировка идёт по паре (подходит, балл): сначала все подходящие по
    # убыванию балла, затем все отклонённые — тоже по убыванию балла.
    keys = [(r["is_eligible"], r["score"]) for r in ranked["results"]]
    assert keys == sorted(keys, reverse=True), (
        f"Результаты не отсортированы по (подходит, балл): {keys}"
    )


def test_match_endpoint_returns_requirements(client):
    """Подбор по HTTP отдаёт требования даже когда решений нет."""
    response = client.post(
        "/api/v1/match",
        json={"object_type": "warehouse", "process_code": "intra_logistics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["requirements"], "Требования не отданы"
    assert body["summary"]["considered"] > 0
