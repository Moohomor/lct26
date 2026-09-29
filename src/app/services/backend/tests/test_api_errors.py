"""Ошибки API видны пользователю, а не глотаются.

Здесь проверяется то, что интерфейс показывает при отказе. Проверки
успешных сценариев этот класс ошибок не ловят: регистрация с нормальным
паролем проходит, и о том, что при негодном пароле форма молчит, узнать
можно было только вручную.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")


def test_trivial_password_is_rejected_with_readable_text(client):
    """Пароль только из букв или только из цифр — с объяснением на русском.

    Текст приходит из ctx.error: в msg pydantic пишет «Value error, ...»,
    а без перевода пользователь видел служебный префикс и английское имя
    поля.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "novalid@example.com", "password": "abcdefgh"},
    )
    assert response.status_code == 422, f"ожидался 422, получен {response.status_code}"
    body = response.json()
    assert body["code"] == "validation_error"
    assert "только из букв" in body["message"], body["message"]
    assert "Value error" not in body["message"], "служебный префикс pydantic попал в ответ"
    assert "password" not in body["message"], "имя поля на английском в сообщении"


def test_short_password_names_the_field_in_russian(client):
    """Ограничение длины без своего текста — тоже по-русски и с названием поля."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "short@example.com", "password": "a1b2c3d"},
    )
    assert response.status_code == 422
    body = response.json()
    assert "пароль" in body["message"], body["message"]
    assert "String should have" not in body["message"], "английский текст pydantic в ответе"


def test_bad_email_is_rejected_in_russian(client):
    """Почта без знака @ объясняется по-русски, а не строкой библиотеки."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "не-почта", "password": "parol12345"},
    )
    assert response.status_code == 422
    message = response.json()["message"]
    assert "@-sign" not in message and "must have" not in message, message


def test_wrong_password_does_not_leak_user_existence(client):
    """Неверный пароль и несуществующая почта дают одинаковый ответ.

    Разные сообщения позволяют перебором узнать, какие учётные записи
    заведены.
    """
    wrong_password = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "неправильный"},
    )
    no_such_user = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody-here@example.com", "password": "неправильный"},
    )
    assert wrong_password.status_code == 401
    assert no_such_user.status_code == 401
    assert wrong_password.json()["message"] == no_such_user.json()["message"]


def test_error_payload_always_has_all_fields(client):
    """У ответа об ошибке есть код, текст и подсказка.

    Интерфейс показывает `message`, а `hint` объясняет, что делать.
    Ответ без этих полей отрисовывается пустой строкой — так и случилось,
    когда тело ошибки не доходило до клиента.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "novalid2@example.com", "password": "abcdefgh"},
    )
    body = response.json()
    for field in ("code", "message", "hint"):
        assert body.get(field), f"в ответе об ошибке нет «{field}»: {body}"
