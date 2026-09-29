"""Фотографии решений из «Каталога внедрения» ФЦ БАС.

Снимки — часть витрины: без них карточка в каталоге пустая. Здесь
проверяется, что привязка не разъезжается с манифестом, что файлы на
месте, и что адрес в API действительно ведёт к картинке.
"""

from __future__ import annotations

import json
import pytest
from sqlalchemy import select

pytest.importorskip("sqlalchemy")


def test_manifest_matches_assets_on_disk():
    """Каждой записи манифеста соответствует файл на диске."""
    from app.core.config import settings

    path = settings.assets_dir / "solution_photos.json"
    assert path.exists(), f"нет манифеста {path.name}"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert len(manifest) > 50, f"в манифесте всего {len(manifest)} записей"

    missing = [rel for rel in manifest.values() if not (settings.assets_dir / rel).exists()]
    assert not missing, f"файлы не найдены: {missing[:5]}"


def test_photos_assigned_to_solutions(db_session):
    """Часть позиций каталога имеет снимок, и он из манифеста."""
    from app.core.config import settings
    from app.models import Solution

    manifest = json.loads(
        (settings.assets_dir / "solution_photos.json").read_text(encoding="utf-8")
    )
    in_db = {s.photo_file for s in db_session.scalars(select(Solution)) if s.photo_file}
    in_manifest = set(manifest.values())

    assert in_db, "ни у одной позиции нет фотографии — импорт не отработал"
    assert in_db <= in_manifest, f"в базе пути, которых нет в манифесте: {in_db - in_manifest}"


def test_photo_import_is_idempotent(db_session):
    """Повторный импорт не меняет число позиций со снимком."""
    from app.models import Solution
    from app.services.importers.solution_photos import import_solution_photos
    from sqlalchemy import func

    def count() -> int:
        return db_session.scalar(
            select(func.count()).select_from(Solution).where(Solution.photo_file.isnot(None))
        ) or 0

    before = count()
    import_solution_photos(db_session)
    db_session.commit()
    assert count() == before, f"было {before}, стало {count()}"


def test_catalog_returns_working_photo_url(client):
    """Ссылка из ответа каталога действительно отдаёт картинку."""
    items = client.get("/api/v1/catalog", params={"limit": 60}).json()["items"]
    with_photo = [i for i in items if i.get("photo_url")]
    assert with_photo, "в первой странице каталога нет ни одной фотографии"

    # Забираем через сам TestClient: «testserver» не разрешается в DNS,
    # urlopen здесь не годится.
    for item in with_photo[:3]:
        assert item["photo_url"].startswith("/static/")
        response = client.get(item["photo_url"])
        assert response.status_code == 200, f"{item['photo_url']} -> {response.status_code}"
        assert response.headers["content-type"] in {"image/jpeg", "image/png", "image/webp"}
        assert len(response.content) > 1000


def test_items_without_photo_have_null(client):
    """Позиция без снимка отдаёт null, а не пустую ссылку."""
    items = client.get("/api/v1/catalog", params={"limit": 60}).json()["items"]
    for item in items:
        url = item.get("photo_url")
        assert url is None or url.startswith("/static/"), f"кривая ссылка: {url!r}"
