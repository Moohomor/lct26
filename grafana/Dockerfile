# Grafana «как есть» из docker-compose.yml.
# Render собирает сервисы из Dockerfile в репозитории, поэтому
# используем официальный образ Grafana как базовый.
#
# Провизнинг и данные в git не хранятся (см. .gitignore → grafana/),
# поэтому конфигурация задаётся переменными окружения на стороне Render.

FROM grafana/grafana:latest

# Render требует, чтобы сервис слушал порт из $PORT, а Grafana — порт 3000.
# Вместо dockerCommand (Render разбирает его без shell) используем свой
# entrypoint, который подставляет $PORT в GF_SERVER_HTTP_PORT.
COPY --chmod=755 start.sh /start.sh
# (без RUN chmod: у образа grafana/grafana жёсткая корневая ФС —
#  обычный chmod в RUN не проходит из-за Operation not permitted)

ENTRYPOINT ["/start.sh"]

EXPOSE 3000