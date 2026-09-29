"""Админские ручки отвечают, а не падают.

Обе проверки ловят один класс ошибок: run_seed возвращает dataclass
SeedReport, и обращение к нему как к словарю (result.get(...)) роняет
ручку в 500. Так было в автозапуске при старте и в POST /admin/seed —
один и тот же баг в двух местах.
"""

from __future__ import annotations

import pytest
from sqlalchemy import select

pytest.importorskip("sqlalchemy")


def test_admin_seed_endpoint_answers(client, admin_headers):
    """POST /admin/seed отвечает 200 и возвращает сводку, а не 500."""
    response = client.post("/api/v1/admin/seed", headers=admin_headers)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["ok"] is True
    # summary обязан быть словарём со счётчиками: на нём держится отчётность
    # о состоянии данных в админке.
    assert isinstance(body["summary"], dict)
    assert body["summary"]["solutions"] > 0
    assert body["summary"]["object_types"] > 0
    assert isinstance(body["warnings"], list)


def test_admin_seed_is_idempotent(client, admin_headers, db_session):
    """Повторный запуск без force не меняет число решений."""
    from app.models import Solution
    from sqlalchemy import func

    before = db_session.scalar(select(func.count()).select_from(Solution)) or 0
    response = client.post("/api/v1/admin/seed", headers=admin_headers)
    assert response.status_code == 200, response.text
    after = db_session.scalar(select(func.count()).select_from(Solution)) or 0
    assert after == before, f"решений было {before}, стало {after}"


def test_seed_report_has_no_dict_access(db_session):
    """SeedReport — dataclass: код не должен ждать от него .get()."""
    from app.seed.seed import SeedReport

    report = SeedReport()
    assert not hasattr(report, "get"), (
        "у SeedReport появился .get: значит вызывающий код перестанет "
        "падать там, где раньше был 500"
    )
    assert isinstance(report.as_dict(), dict)
