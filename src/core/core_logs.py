from sys import stdout
from datetime import datetime
from pathlib import Path
from loguru import logger


def init_log(log_level_file="INFO", log_level_std="WARNING"):
    try:
        logger.remove()
        Path("./data/logs").mkdir(exist_ok=True, parents=True)
        current_date = datetime.now().strftime("%Y-%m-%d")
        logger.add(
            "./data/logs" / "app_" + current_date + ".log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="256 MB",
            retention="10 days",
            level=log_level_file,
            compression="zip",
            enqueue=True,
        )
        logger.add(
            stdout,
            level=log_level_std,
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        )
    except Exception as err:
        logger.error(f"Ошибка инициализации логирования: {err}")