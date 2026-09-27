#!/usr/bin/env bash
# Полная пересборка локальной базы: схема по моделям + загрузка данных организатора.
#
# Нужна при изменении моделей до первого коммита: начальная миграция
# генерируется заново, а не дополняется второй, потому что история схемы
# в репозитории ещё не опубликована.
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="${VENV_PY:-/home/user/robotics-analysis-platform/.venv/bin/python}"
PG_CONTAINER="${PG_CONTAINER:-robotics-analysis-platform-pgsql-1}"
PG_USER="${PG_USER:-root}"
PG_DB="${PG_DB:-robotics}"
export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://${PG_USER}:123456@localhost:5432/${PG_DB}}"

cd "$BACKEND_DIR"
rm -f alembic/versions/*.py
"$VENV_PY" -m alembic revision --autogenerate -m "initial schema"
"$VENV_PY" -m alembic upgrade head
"$VENV_PY" -m app.scripts.db reset --force
"$VENV_PY" -m app.scripts.db seed --force
