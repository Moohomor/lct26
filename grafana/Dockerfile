# Grafana «как есть» из docker-compose.yml.
# Render собирает сервисы из Dockerfile в репозитории, поэтому
# используем официальный образ Grafana как базовый.
#
# Провижининг и данные в git не хранятся (см. .gitignore → grafana/),
# поэтому конфигурация задаётся переменными окружения на стороне Render.
FROM grafana/grafana:latest

# Порт из переменной окружения PORT подставляет Render в рантайме;
# см. dockerCommand в render.yaml (GF_SERVER_HTTP_PORT=$PORT).
EXPOSE 3000