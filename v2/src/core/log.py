import sys
from pathlib import Path
from loguru import logger
from src.core.configs import LOGS_DIR


def init_log(log_level_file="INFO", log_level_std="WARNING"):
    try:
        logger.remove()
        log_dir = Path(LOGS_DIR)
        log_dir.mkdir(exist_ok=True)
        logger.add(
            log_dir / "app_"+date+".log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="256 MB",
            retention="10 days",
            level=log_level_file,
            compression="zip",
            enqueue=True,
        )
        logger.add(
            sys.stdout,
            level=log_level_std,
            colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        )
    except Exception as err:
        logger.error(f"Ошибка инициализации логирования: {err}")
        sys.exit(1)
