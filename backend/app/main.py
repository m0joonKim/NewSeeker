from fastapi.routing import APIRoute
import sentry_sdk
from fastapi import FastAPI
# from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import Column, Integer
import requests

from app.api.main import api_router
from app.core.config import settings
from app.api.routes import login, private, users, newspaper, category, alarm, interactions, utils, auth_social, stat, dashboard



def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix="/api")
app.include_router(newspaper.router, prefix="/api")
app.include_router(alarm.router, prefix="/api")
app.include_router(category.router, prefix="/api")
app.include_router(stat.router, prefix="/api")
# app.include_router(interactions.router, prefix="/api")
app.include_router(login.router, prefix="/api")
app.include_router(users.router, prefix="/api")
# app.include_router(private.router, prefix="/api")
app.include_router(utils.router, prefix="/api")
app.include_router(auth_social.router, prefix="/api")
