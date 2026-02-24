import os
from loguru import logger

from data.config_modules.config_init import config_path


def check_config_exist():
    if os.path.exists(config_path):
        return True
    else:
        return False


def check_folder_path(folder_path):
    if os.path.exists(folder_path):
        return True
    else:
        try:
            os.mkdir(folder_path)
            logger.success(f"Путь создан: {folder_path}")
            return True
        except Exception as err:
            logger.error(f"Ошибка создания пути конфигов: {err}")
            exit()
