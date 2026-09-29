"""Точка входа FastAPI.

Порядок при старте важен:
1. схема приводится к актуальному состоянию (alembic upgrade);
2. данные организатора досеиваются идемпотентно — на Render база живёт
   около месяца, поэтому приложение обязано восстановить её само;
3. обработчики ошибок подключаются последними, чтобы перехватывать всё.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.core.errors import AppError, register_exception_handlers

logger = logging.getLogger("app")
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)

DESCRIPTION = """
Backend платформы подбора роботизированных решений с расчётом
экономического эффекта и визуализацией.

* Справочники типов объектов, параметров и решений открыты для гостя.
* Проекты, расчёты и имитации — для авторизованного пользователя.
* Управление справочниками и нормативами — для администратора.

Расчёт воспроизводим: каждый результат хранит версии модели, каталога и
справочника параметров, а также снимок входных данных.
""".strip()

TAGS_METADATA = [
    {"name": "Аутентификация", "description": "Регистрация, вход, профиль."},
    {"name": "Справочники", "description": "Типы объектов, параметры, процессы, типы решений, вендоры, нормативы."},
    {"name": "Каталог решений", "description": "Позиции каталога с фильтрами и карточками."},
    {"name": "Проекты", "description": "Проекты, подборки решений, сценарии расчёта."},
    {"name": "Подбор решений", "description": "Требования к решениям и балльная оценка пригодности."},
    {"name": "Экономические расчёты", "description": "CAPEX, OPEX, RaaS, TCO, анализ чувствительности."},
    {"name": "Имитация", "description": "Раскладка, KPI и расписание задач для визуализации."},
    {"name": "Администрирование", "description": "Нормативы, параметры, пользователи, импорт данных."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    started = time.perf_counter()
    _migrate()
    _seed_if_needed()
    app.state.startup_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "%s %s готов за %s мс (БД: %s)",
        settings.app_name,
        settings.app_version,
        app.state.startup_ms,
        engine.url.render_as_string(hide_password=True),
    )
    yield
    engine.dispose()


def _migrate() -> None:
    """Приводит схему к актуальному состоянию.

    Отдельным процессом (`alembic upgrade head`), а не `create_all`: в
    конкурентной версии несколько экземпляров стартуют одновременно, и
    `create_all` молча пропустит уже созданные таблицы, оставив схему
    неполной без единой ошибки.
    """
    from alembic import command
    from alembic.config import Config

    from app.core.config import BACKEND_ROOT

    cfg_path = BACKEND_ROOT / "alembic.ini"
    if not cfg_path.exists():
        logger.warning("alembic.ini не найден — миграции пропущены")
        return
    cfg = Config(str(cfg_path))
    # В alembic.ini script_location задан относительным путём, а alembic
    # разрешает его от текущего каталога, а не от расположения ini. При запуске
    # не из корня backend'а миграции молча падают с «Path doesn't exist: alembic»
    # и схема остаётся в состоянии прошлого деплоя.
    cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.sqlalchemy_url)
    try:
        command.upgrade(cfg, "head")
    except Exception as exc:  # noqa: BLE001
        logger.error("Не удалось применить миграции: %s", exc)


def _seed_if_needed() -> None:
    from app.seed.seed import is_seeded, run_seed, seed_summary

    db = SessionLocal()
    try:
        if is_seeded(db):
            logger.info("Данные организатора уже загружены — импорт пропущен")
            return
        logger.info("Загружаю данные организатора…")
        # run_seed возвращает dataclass SeedReport, у которого нет метода get().
        # Сводку берём из seed_summary() — она читает те же таблицы, но после
        # коммита и в том же виде, в каком её показывает админка.
        report = run_seed(db)
        for warning in report.warnings:
            logger.warning("Импорт данных: %s", warning)
        logger.info("Импорт завершён: %s", seed_summary(db))
    except Exception as exc:  # noqa: BLE001
        # Приложение должно подняться даже без данных: справочники при этом
        # пустые, но объяснение пользователю понятнее, чем 502.
        logger.error("Импорт данных не удался: %s", exc)
    finally:
        db.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")

# Фотографии решений из «Каталога внедрения» ФЦ БАС раздаются как статика.
# Монтируется только каталог solutions: шрифты для PDF лежат рядом, но
# отдавать их наружу незачем.
app.mount(
    "/static",
    StaticFiles(directory=settings.assets_dir / "solutions"),
    name="static",
)


@app.middleware("http")
async def timing(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = str(int((time.perf_counter() - started) * 1000))
    return response


@app.get("/health", tags=["Служебные"], summary="Проверка готовности")
def health() -> dict[str, Any]:
    """Проверка готовности: отвечает только при рабочей базе.

    Одной проверки процесса мало: на Render инстанс поднимается раньше базы,
    и «живой» контейнер без соединения к PostgreSQL бесполезен.
    """
    from sqlalchemy import text

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
        detail: str | None = None
    except Exception as exc:  # noqa: BLE001
        db_ok = False
        detail = str(exc)[:200]
    finally:
        db.close()
    return {
        "status": "ok" if db_ok else "degraded",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "ok" if db_ok else f"error: {detail}",
        "startup_ms": getattr(app.state, "startup_ms", None),
    }


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "api": "/api/v1",
    }


@app.exception_handler(404)
async def not_found(_: Request, exc: Any) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "code": "not_found",
            "message": "Метод не найден.",
            "hint": "Список доступных методов — на /docs.",
        },
    )
