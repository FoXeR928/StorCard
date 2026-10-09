import os
import tomllib
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logger_config import init_log

os.makedirs(Path("./data/logs"), exist_ok=True)  #создать через докер

IS_DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
init_log(is_debug=IS_DEBUG)

from db.db_create import Base, engine

from api.api_auth import auth_app
from api.api_users import users_app
from api.api_cards import cards_app


def load_project_metadata():
    """Считывает имя и версию проекта напрямую из pyproject.toml"""
    try:
        with open("./pyproject.toml", "rb") as file:
            data = tomllib.load(file)
        project = data.get("project", {})
        return project.get("name", "storcard"), project.get("version")
    except Exception as err:
        logger.error(f"Ошибка чтения метаданных pyproject.toml: {err}")
        return "storcard", '0'

APP_NAME, APP_VERSION = load_project_metadata()
APP_PORT=int(os.getenv("APP_PORT", 8000))

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: выполняется один раз при старте контейнера"""
    logger.info(f"Запуск {APP_NAME} v{APP_VERSION}: проверка базы данных SQLite...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.success("Инфраструктура базы данных полностью готова к работе.")
    except Exception as e:
        logger.critical(f"Критическая ошибка при инициализации сервера: {e}")
        raise e
    yield
    logger.info("Сервер StorCard успешно остановлен.")

app = FastAPI(
    title="StorCard API",
    description="Ультра-легкий Headless-бэкенд для хранения и синхронизации дисконтных карт",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if IS_DEBUG else None,
    redoc_url="/redoc" if IS_DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Запрос: {request.method} {request.url.path} | "
        f"Статус: {response.status_code} | "
        f"Время: {process_time:.2f}ms"
    )
    return response

app.include_router(auth_app)
app.include_router(users_app)
app.include_router(cards_app)

@app.get("/status", summary="Проверка работоспособности сервера")
async def get_status_api():
    return {
        "status": "OK",
        "app": APP_NAME,
        "version": APP_VERSION
    }
if __name__ == "__main__":
    logger.success(
        f"\n=========================================================\n"
        f" Сервер успешно запущен и готов к работе!\n"
        f" Порт используется: {APP_PORT}\n"
        f"========================================================="
    )
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=APP_PORT, 
        reload=IS_DEBUG,
        log_level="warning" 
    )