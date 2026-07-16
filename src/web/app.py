from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sys import exit
from core.core_config import APP_NAME, APP_DESCRIPTION, APP_VERSION
from database.db_engine import init_db_async
from web.api.api_auth import api_auth
from web.api.api_users import api_users
from web.api.api_cards import api_cards


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db_async()
    except Exception as err:
        logger.critical(f"Не удалось запустить lifespan базы данных: {err}")
        raise e
    yield


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    summary="Сервер StorCard",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    app.include_router(api_auth)
    app.include_router(api_users)
    app.include_router(api_cards)
    logger.info("API успешно инициализировано")
except Exception as e:
    logger.exception(f"Критическая ошибка при инициализации роутеров: {e}")
    exit(1)


@app.get("/status", summary="Проверка сервера", tags=["System"])
async def get_status_api():
    return {"status": "OK", "app": APP_NAME, "version": APP_VERSION}
