"""Единый формат ошибок API.

ТЗ 4.5.4: ошибки формулируются понятным языком и содержат способ исправления,
поэтому тело ошибки — это {"code", "message", "hint", "details"}.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    """Ошибка предметной области с понятным сообщением для пользователя."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "app_error",
        hint: str | None = None,
        details: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.hint = hint
        self.details = details
        self.status_code = status_code


def _payload(code: str, message: str, hint: str | None = None, details: Any = None) -> dict[str, Any]:
    body: dict[str, Any] = {"code": code, "message": message}
    if hint:
        body["hint"] = hint
    if details is not None:
        body["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(exc.code, exc.message, exc.hint, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "message" in detail:
            return JSONResponse(status_code=exc.status_code, content=detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_payload(f"http_{exc.status_code}", str(detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        first = exc.errors()[0] if exc.errors() else {}
        loc = ".".join(str(p) for p in first.get("loc", [])[1:]) or "тело запроса"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_payload(
                "validation_error",
                f"Проверьте значение поля «{loc}»: {first.get('msg', 'некорректное значение')}",
                hint="Сверьтесь с единицами измерения и допустимым диапазоном поля.",
                details=exc.errors(),
            ),
        )
