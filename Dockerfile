FROM python:3.14

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt \
    && pip install uv

# CMD ["uv", "run", "fastapi", "dev", "src/app/services/backend/main.py", "--port", "5000"]

# Если запускаете за прокси, например Nginx или Traefik, добавьте --proxy-headers
# CMD ["fastapi", "run", "dev", "app/main.py", "--port", "80", "--proxy-headers"]