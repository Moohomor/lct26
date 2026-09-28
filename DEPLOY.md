# Развёртывание

Два независимых способа запустить одно и то же: локально через compose и
в облаке на Render. Оба поднимают один и тот же код из одного репозитория.

---

## 1. Локально через docker compose

Нужен только Docker. Ни Python, ни Node.js ставить не нужно — всё внутри
образов.

```bash
git clone <url-репозитория> robotics-analysis-platform
cd robotics-analysis-platform
docker compose up -d
```

Через полминуты-минуту поднимается:

| Что | Адрес |
|---|---|
| API и документация | http://localhost:5000/docs |
| Фронтенд | http://localhost:8080 |
| Grafana | http://localhost:8083 (admin / 123456) |
| PostgreSQL | `localhost:5432`, база `robotics`, пользователь `root` / `123456` |

### Что происходит при первом старте

1. Применяются миграции Alembic (`alembic upgrade head`).
2. Если база пустая, загружаются данные организатора: типы объектов,
   параметры из `Датасеты_хакатон.xlsx`, каталог решений из
   `catalog_export_v4.csv`, нормативы, вендоры, демо-аккаунты.

Проверить, что всё поднялось:

```bash
curl http://localhost:5000/health
# {"status":"ok", ..., "database":"ok", "startup_ms":2752}
```

`status: degraded` означает, что процесс жив, но база недоступна.

### Демо-доступы

| Роль | Логин | Пароль |
|---|---|---|
| Администратор | `admin@example.com` | `demo12345` |
| Пользователь | `user@example.com` | `demo12345` |

### Полезные команды

```bash
docker compose logs -f api        # логи бэкенда
docker compose down               # остановить
docker compose down -v            # остановить и стереть базу
docker compose up -d --build api  # пересобрать только бэкенд
```

### Переменные окружения

Значения по умолчанию зашиты в `docker-compose.yml` и подходят для разработки.
Чтобы задать свои, создайте `.env` (шаблон — [`.env.example`](./.env.example)):

```bash
cp .env.example .env
```

---

## 2. На Render

Render сам собирает образы из Dockerfile. Манифест — [`render.yaml`](./render.yaml),
это аналог `docker-compose.yml`.

### Вариант A. Blueprint (создаёт всё сразу)

Подходит, если базы ещё нет — самый быстрый путь для нового человека.

1. Залейте код в репозиторий на GitHub.
2. Render Dashboard → **New + → Blueprint** → выберите репозиторий.
3. Render создаст четыре ресурса: `api` (web, Docker), `grafana` (web, Docker),
   статический сайт `robotics-analysis-platform` и PostgreSQL `pgsql`.
4. Задайте `NUXT_PUBLIC_API_BASE` у статического сайта — адрес API вида
   `https://<slug-бэкенда>.onrender.com`. Render спросит при создании.
5. Задайте `FRONTEND_ORIGINS` у `api`, если фронтенд доступен не по дефолтному
   адресу: `https://<slug-фронтенда>.onrender.com`.

`SECRET_KEY` создастся автоматически. **Без него JWT подписываются строкой
`dev-secret-change-me-in-production` из кода — переопределите.**

#### Про скорость сборки

`requirements.txt` в режиме `--require-hashes`: как только у одного пакета
есть хеш, pip требует хеши у всех, включая транзитивные зависимости. Поэтому
список должен содержать их явно.

Хеши перечислены для **всех** файлов релиза (sdist и колёса всех платформ).
Это не перестраховка, а необходимость: если оставить только колёса под одну
платформу, то при смене версии Python в образе или при сборке на другой ОС
pip не найдёт подходящего колеса, скачает sdist и будет компилировать пакет
— на Render это превращает сборку в десятки минут.

Если меняете версии зависимостей, не правьте файл руками:

```bash
python scripts/regenerate_requirements.py
```

Скрипт берёт версии из текущего файла и заново проставляет хеши со всех
файлов релиза.

### Вариант B. Переиспользовать существующую базу

Если база `pgsql` уже создана и в ней есть пользователи, проекты и расчёты,
её удалять не нужно. Блок `databases:` в `render.yaml` заставит Render
создать **новую** базу, поэтому:

1. Создайте сервисы из этого же репозитория, но удалите из `render.yaml`
   блок `databases:` (от `databases:` до конца файла).
2. У сервиса `api` задайте `DATABASE_URL` вручную:
   Dashboard → `pgsql` → **Connection** → **Internal Database URL**.

Приложение само поднимет схему и загрузит данные, но уже существующие
данные сохранятся.

### Проверка после деплоя

```bash
# 1. Заголовок в /openapi.json показывает имя приложения, а не «FastAPI».
#    Если здесь FastAPI/0.1.0 — запущена не та точка входа.
curl -s https://<api>.onrender.com/openapi.json | head -c 120

# 2. Схема создана и база отвечает
curl -s https://<api>.onrender.com/health

# 3. Справочник отдаёт данные, а не пустой массив
curl -s https://<api>.onrender.com/api/v1/object-types | head -c 200
```

Должно быть 51 путь и 61 операция в `/docs`.

### На что смотреть в логах

```
Running upgrade  -> 33f3b72b2055, initial schema     ← миграции прошли
Импорт завершён: {'object_types': 3, 'parameters': 138, ...}  ← данные загрузились
... готов за 2752 мс (БД: postgresql+psycopg://...)
```

Сообщение `Импорт данных не удался` при пустой базе означает, что датасет не
подхватился — проверьте, что `app/seed/data/Датасеты_хакатон.xlsx` попал в образ
(в `.dockerignore` он не исключён).

### Ограничения бесплатного плана

- Free-веб-сервисы засыпают после ~15 минут простоя, следующий запрос
  поднимает их заново (30–60 секунд).
- **Free PostgreSQL удаляется через ~30 дней.** Данные при этом не пропадают
  бесплатно: приложение при старте прогонит миграции и заново загрузит данные
  организатора, но пользователи, проекты и расчёты придётся заводить заново.
  Для постоянного хранения нужен платный план.
- Grafana на free-плане не переживает перезапуск (нужен Disks).

---

## 3. Датасет организатора

`src/app/services/backend/app/seed/data/Датасеты_хакатон.xlsx` — источник
типов объектов и их параметров. Книга в репозитории, отдельного шага при
установке не требует: при первом старте она импортируется сама.

Четыре листа, три из них — данные:

| Лист | Тип объекта | Параметров |
|---|---|---|
| Склад | `warehouse` | 42 |
| Аэропорт | `airport` | 39 |
| Медучреждение | `medical` | 57 |
| Легенда и использование | — | документация, не импортируется |

Всего 138 параметров в 24 группах.

Если книгу заменили, посмотрите, что в ней, и сверьте с базой:

```bash
cd src/app/services/backend

# Что лежит в книге
python -m scripts.import_dataset

# Сверка книги с базой; код 1 означает расхождение
python -m scripts.import_dataset --check

# Переимпорт (идемпотентный — повторный запуск не плодит дубликаты)
python -m scripts.import_dataset --import
```

Переменные берутся из окружения, поэтому для нестандартной базы:

```bash
DATABASE_URL='postgresql+psycopg://root:123456@localhost:5432/robotics' \
  python -m scripts.import_dataset --check
```

В CI тот же `--check` ловит расхождение между книгой и базой до деплоя.

---

## 4. Тесты

Тесты работают на настоящей базе, а не на заглушках, и требуют её prepared
состояния:

```bash
createdb robotics_test
cd src/app/services/backend
DATABASE_URL='postgresql+psycopg://root:123456@localhost:5432/robotics_test' \
  python -m alembic upgrade head
DATABASE_URL='postgresql+psycopg://root:123456@localhost:5432/robotics_test' \
  python -c "from app.core.db import SessionLocal; from app.seed.seed import run_seed; \
             db=SessionLocal(); run_seed(db); db.close()"

python -m pytest tests -q
```

Без предварительно загруженных данных `client`-фикстура пропустит часть
тестов, а тесты, которым нужен прямой доступ к моделям, упадут на
`relation "object_types" does not exist`.
