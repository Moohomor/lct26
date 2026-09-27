"""Конфигурация приложения (env → pydantic-settings).

Все настройки читаются из переменных окружения, поэтому одна и та же сборка
работает локально (docker compose) и в облаке (Render).
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Этот файл лежит в backend/app/core/config.py, поэтому до корня backend'а
# нужно подняться на три уровня.
BACKEND_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = BACKEND_ROOT / "app"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Приложение ────────────────────────────────────────────────────────
    app_name: str = "Платформа подбора роботизированных решений"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── База данных ───────────────────────────────────────────────────────
    # В compose не задаётся — собираем из отдельных переменных pgsql.
    database_url: str = ""
    postgres_user: str = "root"
    postgres_password: str = "123456"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "robotics"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # ── Безопасность ──────────────────────────────────────────────────────
    secret_key: str = Field(default="dev-secret-change-me-in-production")
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60 * 12
    refresh_token_ttl_days: int = 30

    # ── CORS ──────────────────────────────────────────────────────────────
    frontend_origins: str = ""

    # ── Бизнес-настройки ──────────────────────────────────────────────────
    calc_model_version: str = "econ-1.0.0"
    default_horizon_years: int = 5
    auto_seed_on_startup: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def _blank_to_empty(cls, v: str) -> str:
        return v or ""

    @property
    def sqlalchemy_url(self) -> str:
        """Итоговый DSN: явный DATABASE_URL имеет приоритет над POSTGRES_*."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        origins = [
            "http://localhost:8080",
            "http://localhost:3000",
            "http://127.0.0.1:8080",
            "http://127.0.0.1:3000",
            "https://robotics-analysis-platform.onrender.com",
        ]
        origins += [o.strip() for o in self.frontend_origins.split(",") if o.strip()]
        # убираем дубли, сохраняя порядок
        return list(dict.fromkeys(origins))

    @property
    def seed_data_dir(self) -> Path:
        return APP_DIR / "seed" / "data"

    @property
    def assets_dir(self) -> Path:
        return APP_DIR / "assets"

    @property
    def uploads_dir(self) -> Path:
        return BACKEND_ROOT / "uploads"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
