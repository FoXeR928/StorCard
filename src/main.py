import uvicorn
from loguru import logger
from database.db_engine import init_db
from core.core_logs import init_log
from core.core_config import PORT, log_level
from web.app import app


def start_app():
    try:
        init_log(log_level_std=log_level)
        init_db()
        logger.info("Конфигурация загружена из БД")
    except Exception as e:
        logger.error(f"Ошибка загрузки конфига из БД: {e}.")
    try:
        logger.success(f"Сервер запускается на 0.0.0.0:{PORT} (Log: {log_level})")
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
