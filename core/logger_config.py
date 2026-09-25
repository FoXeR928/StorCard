import sys
from pathlib import Path
from loguru import logger

def init_log(is_debug: bool):
    """Инициализация ротации и формата логов в папке data"""
    LOG_DIR = Path("./data/logs")
    logger.remove()
    log_level_std = "TRACE" if is_debug else "INFO"
    logger.add(
        sys.stdout, 
        level=log_level_std,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )

    logger.add(
        LOG_DIR / "storcard.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )
