import os
from loguru import logger
import json

from data.config_modules.config_init import config_path, config_folder_path


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


def config_create(data):
    if check_folder_path(config_folder_path):
        with open(config_path, "w") as file_config:
            json.dump(data, file_config, indent=4)
