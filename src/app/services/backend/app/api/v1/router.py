"""Эндпоинты платформы, версия 1.

Роутеры собираются здесь явным списком: при добавлении нового раздела
достаточно дописать одну строку, и он гарантированно попадёт в приложение.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    admin,
    auth,
    catalog,
    economics,
    export,
    matching,
    projects,
    reference,
    simulation,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(reference.router)
api_router.include_router(catalog.router)
api_router.include_router(projects.router)
api_router.include_router(matching.router)
api_router.include_router(economics.router)
api_router.include_router(simulation.router)
api_router.include_router(export.router)
api_router.include_router(admin.router)
