import tomllib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from src.core.constants import PROJECT_FILE, STATIC_DIR
import src.core.config as config


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
            app.include_router(auth_app)
            app.include_router(config_app)
            app.include_router(users_app)
            app.include_router(cards_app)

            if get_config("front"):
                app.mount(
                    "/static", StaticFiles(directory=str(STATIC_DIR)), name="static"
                )
                app.include_router(admin_pages_app)
                app.include_router(auth_pages_app)
                logger.info("Web-интерфейс инициализирован")
        else:
            import src.api.v1.api_install as api_intall
            import src.web.routes.route_install as route_install

            app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
            app.include_router(api_intall.install_api)
            app.include_router(route_install.install_route)
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
