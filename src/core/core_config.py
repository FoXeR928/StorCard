from secrets import token_hex
from os import getenv
from loguru import logger
from importlib.metadata import version, metadata
from pathlib import Path
from sys import exit

DB_DRIVER = getenv("SQL_DRIVER", "sqlite")
DB_NAME = getenv("SQL_DB", "storcard_db")
PORT = getenv("PORT", 7000)
APP_NAME = metadata("storcard")["Name"]
APP_DESCRIPTION = metadata("storcard")["Description"]
APP_VERSION = version("storcard")
ACCESS_TOKEN = getenv("ACCESS_TOKEN", 3600)
REFRESH_TOKEN = getenv("REFRESH_TOKEN", 604800)

DEBUG = getenv("DEBUG", 0)
if DEBUG == 1:
    log_level = "TRACE"
elif DEBUG == 0:
    log_level = "WARNING"
else:
    log_level = "WARNING"
    logger.warning("[WARNING] Неизвестный уровень логировани, установлен 0")

key_file = Path("./data/secret.key")
try:
    if key_file.exists():
        SECRET_KEY = key_file.read_text().strip()
    else:
        SECRET_KEY = token_hex(32)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        key_file.write_text(SECRET_KEY)
except Exception as e:
    logger.critical(f"Ошибка получения секретного ключа: {e}")
    exit(1)