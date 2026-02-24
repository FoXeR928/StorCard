from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import tomllib
from loguru import logger
from data.config_modules.config_check import check_config_exist

def init_pages():
    try:
        if check_config_exist():
            from network.api.api_auth import auth_app
            from network.api.api_config import config_app
            from network.api.api_users import users_app
            from network.api.api_cards import cards_app
            from network.web.admin_pages import admin_pages_app
            from network.web.auth_pages import auth_pages_app
            from data.db_modules.db_query_config import get_config

            app.include_router(router=auth_app)
            app.include_router(router=config_app)
            app.include_router(router=users_app)
            app.include_router(router=cards_app)
            front_status = bool(int(get_config("front")))
            if front_status:
                app.mount(
                    "/static",
                    StaticFiles(directory="network/public/static"),
                    name="front",
                )
                app.include_router(router=admin_pages_app)
                app.include_router(router=auth_pages_app)
                logger.info("Инициализирован Web")
        else:
            from network.api.api_config_start import config_start_app
            from network.web.start_pages import start_pages_app

            app.include_router(router=config_start_app)
            app.include_router(router=start_pages_app)
        logger.debug("Инициализирован API")
    except Exception as err:
        logger.error(f"Ошибка инициализации API: {err}")

if check_config_exist():
    from data.db_modules.db_create_default import (
        create_default_users,
        create_default_config,
    )

    create_default_config()
    create_default_users()

try:
    with open("./pyproject.toml", "rb") as file:
        data = tomllib.load(file)
    project = data.get("project", {})
    app_name = project.get("name")
    app_version = project.get("version")
    logger.info("Информация о приложении получена")
except Exception as err:
    logger.critical(f"Ошибка получения информации о приложении: {err}")
    exit()

try:
    app = FastAPI(
        title="StorCard",
        description="StorCard is your own server for storing discount cards",
        version=app_version,
        summary="Сервер",
    )
except Exception as err:
    logger.critical(f"Ошибка инициализации приложения: {err}")
    exit()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_pages()


@app.get("/status", summary="Проверка сервера")
async def get_status_api():
    return {"status": "OK", "app": app_name, "version": app_version}
