# Robotics Analysis Platform

Платформа подбора роботизированных решений с расчётом экономического
эффекта и визуализацией. Бэкенд — FastAPI, база — PostgreSQL, интерфейс —
Nuxt 4, дашборды — Grafana.

## Что внутри

| Сервис   | Технология            | Локальный порт | На Render            |
|----------|-----------------------|----------------|----------------------|
| `api`    | FastAPI (Python 3.12) | 5000           | `api` (Docker)       |
| `pgsql`  | PostgreSQL 14         | 5432           | `pgsql` (managed)    |
| `nodejs` | Nuxt 4 фронтенд       | 8080 → 3000    | статический сайт     |
| `grafana`| Grafana               | 8083 → 3000    | `grafana` (Docker)   |

API: 51 путь, 61 ручка — аутентификация, справочники, каталог, проекты,
подбор решений, экономические расчёты (CAPEX/OPEX/RaaS/TCO и анализ
чувствительности), имитация, выгрузка PDF, администрирование.

## Быстрый старт

```bash
docker compose up -d
```

- Документация API — http://localhost:5000/docs
- Интерфейс — http://localhost:8080
- Grafana — http://localhost:8083 (`admin` / `123456`)

При первом старте приложение само применит миграции и загрузит данные
организатора: типы объектов, 138 параметров из `Датасеты_хакатон.xlsx`,
каталог решений, нормативы, вендоров и демо-аккаунты.

Демо-доступы: `admin@example.com` / `demo12345` и
`user@example.com` / `demo12345`.

## Документация

- [**DEPLOY.md**](./DEPLOY.md) — подробная инструкция: локально через
  compose и развёртывание на Render, переменные окружения, проверка,
  тесты, работа с датасетом.
- [`render.yaml`](./render.yaml) — манифест Render (аналог compose).
- [`docker-compose.yml`](./docker-compose.yml) — локальный стек.
- [`.env.example`](./.env.example) — шаблон переменных окружения.

## Структура

```
src/app/services/backend/     FastAPI: app/api/v1/routes — ручки,
                              app/models — ORM, app/seed — загрузка
                              данных организатора, alembic — миграции
src/app/services/frontend/    Nuxt 4 (ssr: false, статическая сборка)
grafana/                      дашборды и их provisioning
render.yaml                   манифест Render
docker-compose.yml            локальный стек
```
