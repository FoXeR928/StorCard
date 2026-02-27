import tomllib
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import tomllib
from loguru import logger
from data.config_modules.config_check import check_config_exist
from network.api.api_auth import auth_app
from network.api.api_config import config_app
from network.api.api_users import users_app
from network.api.api_cards import cards_app
from network.web.admin_pages import admin_pages_app
from network.web.auth_pages import auth_pages_app
from data.db_modules.db_query_config import get_config

TEMPLATE_DIR =  "src/web/template"
STATIC_DIR "src/web/static"
PROJECT_PATH =  "pyproject.toml"

def load_app_metadata():
    try:
        with open(PROJECT_PATH, "rb") as f:
            data = tomllib.load(f).get("project", {})
        return data.get("name", "StorCard"), data.get("version", "0.1.0")
    except Exception as e:
        logger.error(f"Ошибка чтения метаданных: {e}")
        return "StorCard", "unknown"

APP_NAME, APP_VERSION = load_app_metadata()

def setup_routes(app: FastAPI):
    try:
        config_exists = check_config_exist()
        
        if config_exists:
            app.include_router(auth_app)
            app.include_router(config_app)
            app.include_router(users_app)
            app.include_router(cards_app)
            
            if get_config("front"):
                app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
                app.include_router(admin_pages_app)
                app.include_router(auth_pages_app)
                logger.info("Web-интерфейс инициализирован")
        else:
            from network.api.api_config_start import config_start_app
            from network.web.start_pages import start_pages_app
            
            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
            app.include_router(config_start_app)
            app.include_router(start_pages_app)
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
    return {
        "status": "OK",
        "app": APP_NAME,
        "version": APP_VERSION
    }