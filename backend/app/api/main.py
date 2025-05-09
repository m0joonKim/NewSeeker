from fastapi import APIRouter

from app.api.routes import login, private, users, utils, alarm, interactions, category, newspaper
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(alarm.router)
api_router.include_router(interactions.router)
api_router.include_router(category.router)
api_router.include_router(newspaper.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
