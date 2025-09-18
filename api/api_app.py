from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from loguru import logger

def init_pages():
    try:
        app.mount("/static", StaticFiles(directory="front/public/static"), name="front")
        if os.path.exists("./instance/config.json") == True:
            from api.api_auth import auth_app
            from api.api_config import config_app
            from api.api_users import users_app
            from api.api_cards import cards_app
            from front.admin_pages import admin_pages_app

            app.include_router(router=auth_app)
            app.include_router(router=config_app)
            app.include_router(router=users_app)
            app.include_router(router=cards_app)
            app.include_router(router=admin_pages_app)
        else:
            from api.api_config_start import config_start_app
            from front.start_pages import start_pages_app

            app.include_router(router=config_start_app)
            app.include_router(router=start_pages_app)
        logger.debug("Инициализирован API")
    except Exception as err:
        logger.error(f"Ошибка инициализации API: {err}")


if os.path.exists("./instance/config.json") == True:
    from db_modules.db_create_default import (
        create_default_users,
        create_default_config,
    )

    create_default_config()
    create_default_users()
try:
    app = FastAPI(
        title="StorCard",
        description="StorCard is your own server for storing discount cards",
        version="0.4.3-alfa",
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
    return {"status":"OK"}