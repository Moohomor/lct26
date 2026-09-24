# Robotics Analysis Platform

Стек (docker-compose.yml):

| Сервис   | Технология            | Локальный порт |
|----------|-----------------------|----------------|
| `api`    | FastAPI (Python 3.14) | 5000           |
| `pgsql`  | PostgreSQL 14         | 5432           |
| `nodejs` | Nuxt 4 фронтенд       | 8080 → 3000    |
| `grafana`| Grafana               | 8083 → 3000    |

## Локально

```bash
docker compose up -d
```

## Деплой на Render (быстрый старт)

Render забирает код из GitHub-репозитория и сам собирает образы.
Готовый манифест: [`render.yaml`](./render.yaml) (аналог docker-compose.yml).

1. Создайте пустой репозиторий на GitHub и залейте туда этот код.
2. В [Render Dashboard](https://dashboard.render.com): **New + → Blueprint**.
3. Подключите GitHub-репозиторий. Render создаст три ресурса:
   - `api` — web-сервис (Docker), FastAPI. Слушает порт из `$PORT`.
   - `grafana` — web-сервис (Docker) на базе образа `grafana/grafana`.
   - `pgsql` — управляемая PostgreSQL.
4. Фронтенд (статический сайт `src/app/services/frontend`) деплоится отдельно:
   **New + → Static Site**, каталог `src/app/services/frontend`,
   команда сборки `yarn; yarn generate`, публикуемый каталог `dist`.

### Переменные окружения

- `api`: `FRONTEND_ORIGINS` — дополнительные CORS-домены через запятую
  (по умолчанию уже разрешён `https://robotics-analysis-platform.onrender.com`).
- `api`: `DATABASE_URL` — подставляется из сервиса `pgsql` автоматически.
- `grafana`: `GF_SECURITY_ADMIN_USER` / `GF_SECURITY_ADMIN_PASSWORD`.

### Ограничения бесплатного плана

- Free-веб-сервисы уходят в сон после ~15 мин простоя (холодный старт).
- Free PostgreSQL удаляется автоматически через ~30 дней.
- Для сохранения данных Grafana нужен платный план (Disks), поэтому
  на free-плане дашборды не переживают перезапуск.