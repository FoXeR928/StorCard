from loguru import logger
import json

config_folder_path = "./instance"
config_path = "./instance/config.json"


def init_confg():
    try:
        with open(config_path, "r") as file_config:
            config = json.load(file_config)
        logger.info("Config file init")
        return config
    except Exception as err:
        logger.critical(f"Config file init failed. Error: {err}")
        exit()

