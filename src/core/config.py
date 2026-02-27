import sys
from loguru import logger

def check_config_exist() -> bool:
    return CONFIG_FILE.exists()

def init_config() -> Dict[str, Any]:
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("Конфигурация успешно загружена")
        return config
    except (FileNotFoundError, json.JSONDecodeError) as err:
        logger.critical(f"Ошибка загрузки конфига: {err}")
        sys.exit(1)

def config_create(data: Dict[str, Any]) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.success(f"Конфигурация создана: {CONFIG_FILE}")
    except Exception as err:
        logger.error(f"Не удалось создать конфиг: {err}")