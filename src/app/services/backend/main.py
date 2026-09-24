import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Дополнительные origin'ы из переменной окружения (через запятую),
# например: FRONTEND_ORIGINS=https://app.onrender.com,https://my-domain.ru
_extra_origins = [
    o.strip()
    for o in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if o.strip()
]

origins = [
    # локальная разработка: docker compose / npm run dev
    "http://localhost:8080",
    "http://localhost:3000",
    # продакшен-фронтенд на Render (статический сайт)
    "https://robotics-analysis-platform.onrender.com",
    *_extra_origins,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/test")
def read_test():
    return {"Hello": "World"}


@app.get("/test-test")
def read_test_test():
    return {"Hello": "World"}