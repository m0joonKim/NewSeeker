from fastapi import APIRouter

from app.api.routes import login, private, users, newspaper, category, alarm, interactions, utils, auth_social
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(newspaper.router)
api_router.include_router(category.router)
api_router.include_router(alarm.router)
api_router.include_router(interactions.router)
api_router.include_router(private.router)
api_router.include_router(utils.router)
api_router.include_router(auth_social.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
