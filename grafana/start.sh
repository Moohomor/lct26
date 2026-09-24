#!/bin/sh
set -e

# Render ожидает, что приложение слушает порт из переменной окружения $PORT,
# а Grafana по умолчанию слушает 3000. Подменяем порт при старте.
export GF_SERVER_HTTP_PORT="${PORT:-3000}"

# Оригинальный entrypoint образа grafana/grafana.
# Аргументы не пробрасываем — Render может передавать сюда dockerCommand,
# который нам не нужен.
exec /run.sh