"""Каталог: фильтры и панель значений.

Фильтры в интерфейсе берутся не из вёрстки, а из /catalog/facets. Если
 facet отдаст не то значение или фильтр начнёт отбрасывать лишнее, позиция
пропадёт из каталога молча — пользователь её просто не увидит.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

pytest.importorskip("sqlalchemy")


def test_facets_cover_every_solution(client):
    """Сумма по отраслям плюс решения без отрасли равны числу позиций.

    Иначе часть каталога не попадёт ни под один фильтр «отрасль» и исчезнет
    из вида, как только пользователь выберет отрасль.
    """
    stats = client.get("/api/v1/catalog/stats").json()
    facets = client.get("/api/v1/catalog/facets").json()

    industries = sum(i["count"] for i in facets["industries"])
    statuses = sum(s["count"] for s in facets["statuses"])
    types = sum(t["count"] for t in facets["solution_types"])
    without = facets["without_industry"]
    shown = stats["total"] - stats["variants"]

    assert industries + without == shown, (
        f"по отраслям {industries} и без отрасли {without}, а показывается {shown}"
    )
    assert statuses == shown, f"по статусам {statuses}, показывается {shown}"
    assert types + without == shown, (
        f"по типам {types} и без отрасли {without}, а показывается {shown}"
    )
    assert without == 0, (
        f"{without} решений без отрасли: они не фильтруются по ней. "
        "Проставьте industry в reference_solutions_seed."
    )


def test_facets_values_are_filterable(client):
    """Каждое значение из facets честно фильтрует каталог."""
    facets = client.get("/api/v1/catalog/facets").json()

    for industry in facets["industries"][:3]:
        found = client.get("/api/v1/catalog", params={"industry": industry["value"]}).json()
        assert found["total"] == industry["count"], (
            f"отрасль {industry['value']!r}: в facets {industry['count']}, "
            f"в фильтре {found['total']}"
        )

    for status in facets["statuses"]:
        found = client.get("/api/v1/catalog", params={"status": status["value"]}).json()
        assert found["total"] == status["count"]

    for st in facets["solution_types"][:3]:
        found = client.get(
            "/api/v1/catalog", params={"solution_type": st["value"]}
        ).json()
        assert found["total"] == st["count"]


def test_industry_filter_returns_only_that_industry(client):
    items = client.get("/api/v1/catalog", params={"industry": "ТЭК"}).json()["items"]
    assert items
    assert {i["industry"] for i in items} == {"ТЭК"}


def test_industry_filter_accepts_several_values(client):
    picked = ["ТЭК", "ЖКХ"]
    found = client.get(
        "/api/v1/catalog", params=[("industry", v) for v in picked]
    ).json()
    assert found["total"] > 0
    assert {i["industry"] for i in found["items"]} <= set(picked)


def test_catalog_list_matches_facet_counts_under_filters(client):
    """Число в выдаче совпадает с объявленным в facets при активном фильтре."""
    facets = client.get("/api/v1/catalog/facets").json()
    top = facets["industries"][0]
    listing = client.get(
        "/api/v1/catalog", params={"industry": top["value"], "limit": 1}
    ).json()
    assert listing["total"] == top["count"]
    assert listing["items"]


def test_hero_count_and_list_count_agree(client):
    """Число, обещанное статистикой, равно тому, что реально в выдаче.

    stats.total включает комплектации, а список их скрывает по умолчанию.
    Страница показывает stats.total − variants; если эти два разойдутся,
    в шапке будет написано одно, а покажется другое.
    """
    stats = client.get("/api/v1/catalog/stats").json()
    listing = client.get("/api/v1/catalog", params={"limit": 1}).json()
    assert listing["total"] == stats["total"] - stats["variants"], (
        f"в списке {listing['total']}, в статистике {stats['total']} "
        f"при {stats['variants']} комплектациях"
    )


def test_facets_do_not_break_detail_route(client):
    """/facets не должен перехватывать /{solution_id}: порядок маршрутов важен."""
    missing = client.get("/api/v1/catalog/00000000-0000-0000-0000-000000000000")
    assert missing.status_code == 404
    item = client.get("/api/v1/catalog", params={"limit": 1}).json()["items"][0]
    assert client.get(f"/api/v1/catalog/{item['id']}").status_code == 200


def test_facets_counts_match_filter_results(client):
    """Счётчик в скобках равен тому, что откроется по клику.

    Список по умолчанию скрывает комплектации. Если facets считает по всей
    таблице, в фильтре написано «28», а приходит 22 — пользователь решает,
    что интерфейс врёт.
    """
    facets = client.get("/api/v1/catalog/facets").json()
    for industry in facets["industries"]:
        found = client.get("/api/v1/catalog", params={"industry": industry["value"]}).json()
        assert found["total"] == industry["count"], (
            f"{industry['value']}: в facets {industry['count']}, в выдаче {found['total']}"
        )


def test_solution_has_no_duplicate_industries(db_session):
    """Названия отраслей не разъезжаются: они же приходят из «Каталога внедрения»."""
    from app.models import Solution

    values = {
        s.industry
        for s in db_session.scalars(select(Solution))
        if s.industry is not None
    }
    normalized = {v.strip() for v in values}
    assert values == normalized, "в отраслях есть значения с лишними пробелами"
