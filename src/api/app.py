import tomllib
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import tomllib
from loguru import logger
import src.core.config as config
from src.core.constants import PROJECT_FILE, STATIC_DIR


def load_app_metadata():
    try:
        with open(PROJECT_FILE, "rb") as f:
            data = tomllib.load(f).get("project", {})
        return data.get("name", "StorCard"), data.get("version", "0.1.0")
    except Exception as e:
        logger.error(f"Ошибка чтения метаданных: {e}")
        return "StorCard", "unknown"


APP_NAME, APP_VERSION = load_app_metadata()


def setup_routes(app: FastAPI):
    try:
        config_exists = config.check_config()

        if config_exists:
            from src.api.v1.api_auth import auth_api
            from src.api.v1.api_config import config_api
            from src.api.v1.api_users import users_api

            app.include_router(auth_api)
            app.include_router(config_api)
            app.include_router(users_api)
            #app.include_router(cards_api)

            from src.database.repository.repo_config import get_config_val

            if bool(int(get_config_val("front_status"))):
                from src.web.routes.route_auth import auth_route
                from src.web.routes.route_admin import admin_route

                app.mount(
                    "/static", StaticFiles(directory=str(STATIC_DIR)), name="static"
                )
                app.include_router(auth_route)
                app.include_router(admin_route)
                logger.info("Web-интерфейс инициализирован")
        else:
            from src.api.v1.api_install import install_api
            from src.web.routes.route_install import install_route

            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
            app.include_router(install_api)
            app.include_router(install_route)
            logger.warning("Конфигурация не найдена: запущен мастер настройки")

        logger.info("API успешно инициализировано")
    except Exception as e:
        logger.exception(f"Критическая ошибка при инициализации роутеров: {e}")


app = FastAPI(
    title=APP_NAME,
    description="Your own server for storing discount cards",
    version=APP_VERSION,
    summary="Сервер StorCard",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_routes(app)


@app.get("/status", summary="Проверка сервера", tags=["System"])
async def get_status_api():
    return {"status": "OK", "app": APP_NAME, "version": APP_VERSION}
