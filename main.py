import uvicorn
import sys
from loguru import logger

from data.config_modules.config_check import check_config_exist
from data.cert_init import init_ssl, cert_folder_path
from data.log_init import init_log
from data.db_modules.db_create import init_db
from data.db_modules.db_query_config import get_all_configs
from data.db_modules.db_create_default import (
    create_default_users,
    create_default_config,
)

def start_app():
    log_level = "INFO"
    if check_config_exist():
        try:
            init_db()
            create_default_config()
            create_default_users()
            conf = get_all_configs() 
            port = int(conf.get("app_port", 7000))
            cert_file = conf.get("cert", "ssl.pem")
            key_file = conf.get("cert_key", "key.pem")
            if conf.get("debug") == "True" or conf.get("debug") == "1":
                log_level = "TRACE"
            init_log(log_level_std=log_level)
            init_ssl(cert_file=cert_file, key_file=key_file)
            logger.info("Конфигурация загружена из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфига из БД: {e}. Используем дефолты.")
    else:
        init_ssl()
        logger.warning("Файл конфигурации не найден, запуск в режиме установки")
    try:
        logger.success(f"Сервер запускается на 0.0.0.0:{port} (Log: {log_level})")
        uvicorn.run(
            app="network.api.api_app:app",
            host="0.0.0.0",
            port=port,
            ssl_certfile=f"{cert_folder_path}/{cert_file}",
            ssl_keyfile=f"{cert_folder_path}/{key_file}",
            log_level=log_level.lower()
        )
    except Exception as err:
        logger.error(f"Критическая ошибка сервера: {err}")
    finally:
        logger.info("Работа сервера завершена")

if __name__ == "__main__":
    start_app()
