"""Карточка решения: варианты комплектации и цена.

Здесь был NameError на несуществующем помощнике `_f`. Он срабатывал
только на решениях, у которых есть варианты комплектации, поэтому
список каталога и карточки большинства позиций открывались нормально —
ошибка выглядела как «иногда карточка не открывается».
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

pytest.importorskip("sqlalchemy")


def _session():
    from app.core.db import SessionLocal

    return SessionLocal()


def test_every_card_opens(client):
    """Карточка каждой позиции каталога отдаётся без ошибки.

    Раньше позиции с вариантами комплектации падали с 500, и это
    зависело от данных, а не от кода запроса, — такой случай ловится
    только перебором.
    """
    listing = client.get("/api/v1/catalog?limit=500").json()
    assert listing["items"], "каталог пуст — проверять нечего"

    broken: list[str] = []
    for item in listing["items"]:
        response = client.get(f"/api/v1/catalog/{item['id']}")
        if response.status_code != 200:
            broken.append(f"{item['name']} → {response.status_code}")
    assert not broken, "карточки не открываются: " + "; ".join(broken[:10])


def test_card_shows_variants(client):
    """Позиция с вариантами комплектации перечисляет их с ценой.

    Цена в БД хранится в Numeric, а схема ждёт float: без приведения
    значение не проходит валидацию ответа.
    """
    from app.models import Solution

    with _session() as db:
        parent_id = db.scalars(
            select(Solution.id)
            .where(Solution.is_variant_of_id.isnot(None))
            .limit(1)
        ).first()
        if parent_id is None:
            pytest.skip("в базе нет вариантов комплектации — нечего проверять")
        expected = db.scalars(
            select(Solution.name).where(Solution.is_variant_of_id == parent_id)
        ).all()

    data = client.get(f"/api/v1/catalog/{parent_id}").json()
    assert len(data["variants"]) == len(expected)
    for variant in data["variants"]:
        assert "id" in variant and "name" in variant
        price = variant["unit_price_rub"]
        assert price is None or isinstance(price, float), (
            f"цена варианта {variant['name']} пришла как {type(price).__name__}, "
            "а не float"
        )


def test_missing_card_is_404_not_500(client):
    import uuid

    response = client.get(f"/api/v1/catalog/{uuid.uuid4()}")
    assert response.status_code == 404, f"ожидался 404, получен {response.status_code}"
