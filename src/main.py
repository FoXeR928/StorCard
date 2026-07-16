import uvicorn
from loguru import logger
from os import getenv
from core.core_logs import init_log
from core.core_config import log_level

init_log(log_level_std=log_level)


def start_app():
    from web.app import app

    try:
        PORT = getenv("PORT", 7000)
        logger.success(f"Сервер запускается на порту: {PORT} (Log: {log_level})")
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=PORT,
            log_level=log_level.lower(),
        )
    except Exception as err:
        logger.error(f"Ошибка Uvicorn: {err}")
    finally:
        logger.info("Работа сервера завершена")


if __name__ == "__main__":
    start_app()
