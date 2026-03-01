import json
import tempfile
import shutil
from typing import Dict, Any
from pathlib import Path
from loguru import logger
from src.core.constants import CONFIG_FILE, DATA_DIR
import src.core.system as system


def check_config() -> bool:
    return CONFIG_FILE.exists()


def get_db_config() -> Dict[str, Any]:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("Конфигурация успешно загружена")
        return config
    except (FileNotFoundError, json.JSONDecodeError) as err:
        logger.critical(f"Ошибка загрузки конфига: {err}")
        system.stop_server(1)


def config_create(data: Dict[str, Any]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w", dir=DATA_DIR, delete=False, encoding="utf-8"
        ) as tf:
            json.dump(data, tf, indent=4, ensure_ascii=False)
            temp_path = Path(tf.name)
        shutil.move(str(temp_path), str(CONFIG_FILE))
        logger.success(f"Конфигурация создана: {CONFIG_FILE}")
    except Exception as err:
        logger.error(f"Не удалось создать конфиг: {err}")
        raise
