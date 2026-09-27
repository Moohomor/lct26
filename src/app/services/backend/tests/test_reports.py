"""PDF-отчёт: файл формируется, доступ проверяется, кириллица на месте.

Проверяется не «функция вернула байты», а три вещи, которые видны пользователю:
файл открывается как PDF, в нём есть русский текст, и чужой расчёт не
скачивается.
"""

from __future__ import annotations

import pytest

pytest.importorskip("reportlab")


def _make_calculation(client, headers) -> int:
    """Создаёт проект с расчётом и возвращает идентификатор расчёта."""
    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"object_type": "warehouse", "name": "Тест отчёта",
               "parameters": {}, "process_codes": ["intra_logistics"]},
    ).json()
    match = client.post(
        f"/api/v1/projects/{project['id']}/match?limit=1", headers=headers
    ).json()
    assert match["added"], "Подбор не добавил решений"
    solutions = client.get(
        f"/api/v1/projects/{project['id']}/solutions", headers=headers
    ).json()
    scenario = client.post(
        f"/api/v1/projects/{project['id']}/scenarios",
        headers=headers,
        json={
            "name": "Покупка",
            "kind": "purchase",
            "items": [{"solution_id": solutions[0]["solution_id"], "quantity": 2}],
        },
    ).json()
    calc = client.post(
        f"/api/v1/scenarios/{scenario['id']}/calculate", headers=headers
    ).json()
    return calc["calculation_id"]


def test_pdf_is_valid_and_contains_cyrillic(client, user_headers):
    """Файл начинается с сигнатуры PDF и содержит зарегистрированные шрифты."""
    calc_id = _make_calculation(client, user_headers)
    response = client.get(
        f"/api/v1/calculations/{calc_id}/export/pdf", headers=user_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    body = response.content
    assert body.startswith(b"%PDF"), "Файл не начинается с сигнатуры PDF"
    # Шрифты DejaVu встроены — без них кириллица превратилась бы в прямоугольники
    assert b"DejaVu" in body, "В PDF нет шрифтов DejaVu"
    # Имя файла должно быть ASCII-транслитом плюс UTF-8 вариант
    disposition = response.headers["content-disposition"]
    assert "filename=" in disposition and "filename*=UTF-8''" in disposition


def test_pdf_requires_authentication(client):
    """Гость не скачает отчёт."""
    response = client.get("/api/v1/calculations/1/export/pdf")
    assert response.status_code == 401


def test_pdf_of_others_calculation_is_forbidden(client, user_headers):
    """Чужой расчёт не отдаётся даже с валидным токеном."""
    calc_id = _make_calculation(client, user_headers)

    # Второй пользователь
    client.post(
        "/api/v1/auth/register",
        json={"email": "stranger@example.com", "password": "test12345"},
    )
    stranger = client.post(
        "/api/v1/auth/login",
        json={"email": "stranger@example.com", "password": "test12345"},
    ).json()["access_token"]

    response = client.get(
        f"/api/v1/calculations/{calc_id}/export/pdf",
        headers={"Authorization": f"Bearer {stranger}"},
    )
    assert response.status_code == 403


def test_inline_pdf_opens_in_browser(client, user_headers):
    """Параметр inline меняет заголовок с attachment на inline."""
    calc_id = _make_calculation(client, user_headers)
    response = client.get(
        f"/api/v1/calculations/{calc_id}/export/pdf?inline=true", headers=user_headers
    )
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("inline")
