from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from core.core_system import stop_server
from src.core.core_config import APP_NAME, APP_VERSION
from src.web.api.v1.api_auth import api_auth_v1
from src.web.api.v1.api_config import api_configs_v1
from src.web.api.v1.api_users import api_users_v1
from src.web.api.v2.api_cards import api_cards_v2


def setup_routes(app: FastAPI):

    from v2.src.api.api.v1.api_auth import auth_api
    from v2.src.web.api.v1.api_config import config_api

    app.include_router(config_api)
    app.include_router(users_api)
    app.include_router(cards_api)

    from src.database.repository.repo_config import get_config_val

    if str(get_config_val("front_status")) == "1":
        from src.web.routes.route_auth import auth_route
        from src.web.routes.route_admin import admin_route

        app.include_router(auth_route)
        app.include_router(admin_route)
        logger.info("Web-интерфейс инициализирован")

        app.include_router(install_api)
        app.include_router(install_route)
        logger.warning("Конфигурация не найдена: запущен мастер настройки")

    logger.info("API успешно инициализировано")


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

if Path(STATIC_DIR).exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

try:
    app.include_router(api_auth_v1)
    app.include_router(api_configs_v1)
    app.include_router(api_users_v1)
    app.include_router(api_cards_v2)
except Exception as e:
    logger.exception(f"Критическая ошибка при инициализации роутеров: {e}")
    stop_server(1)


@app.get("/v1/status", summary="Проверка сервера", tags=["System"])
async def get_status_api():
    return {"status": "OK", "app": APP_NAME, "version": APP_VERSION}
