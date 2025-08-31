from fastapi import FastAPI
from sys import stdout
from loguru import logger

from db_modules.db_create import init_db
from instance.config_read import init_confg
from db_modules.db_create_default import (
    create_default_users,
    create_default_config,
)
from db_modules.db_query_config import get_config


def init_log(log_level_file="INFO", log_level_std="WARNING"):
    logger.remove()
    logger.add(
        "logs/app.log",
        format="{time} | {level} | {message} | {name}",
        rotation="256 MB",
        retention=f"10 days",
        level=log_level_file,
    )
    if bool(int(get_config(name='debug'))) == True:
        log_level_std = "TRACE"
    logger.add(stdout, level=log_level_std)


def init_pages():
    try:
        from api.api_auth import auth_app
        from api.api_config import config_app
        from api.api_users import users_app

        app.include_router(router=auth_app)
        app.include_router(router=config_app)
        app.include_router(router=users_app)
        logger.debug("Инициализирован API")
    except Exception as err:
        logger.error(f"Ошибка инициализации API: {err}")


def init_app():
    try:
        app = FastAPI(
            title="StorCard",
            description="StorCard is your own server for storing discount cards",
            version="0.3.2-alfa",
        )
        return app
    except Exception as err:
        logger.critical(f"Ошибка инициализации приложения: {err}")
        exit()


config = init_confg()
engine = init_db()
create_default_config()
init_log()
create_default_users()
app = init_app()
init_pages()