FROM docker.m.daocloud.io/library/python:3.12

WORKDIR /app

# Зависимости кэшируются отдельно от кода
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Код бэкенда (в compose-файле он монтировался через volume,
# на Render volume'ов нет — копируем код прямо в образ)
COPY src/app/services/backend/ /app/src/app/services/backend/

WORKDIR /app/src/app/services/backend

# Render присылает порт через переменную окружения PORT,
# локально (docker compose) упадём на 5000
EXPOSE 5000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-5000}"]