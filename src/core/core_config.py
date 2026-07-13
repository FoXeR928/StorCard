from os import getenv
from tomllib import load
from loguru import logger

DB_DRIVER = getenv("SQL_DRIVER", "sqlite")
DB_NAME = getenv("SQL_DB", "storcard_db")

try:
    with open("./pyproject.toml", "rb") as file_toml:
        data = load(file_toml).get("project", {})
    APP_NAME = data.get("name", "StorCard")
    APP_VERSION = data.get("version", "0.0.0.0")
except Exception as e:
    logger.error(f"Metadata read error: {e}")
