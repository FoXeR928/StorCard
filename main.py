import uvicorn
from sys import stdout
import os
from loguru import logger

from network.api.api_app import app
from data.config_modules.config_check import check_config_exist
from data.cert_init import init_cert

if check_config_exist():
    from data.db_modules.db_query_config import get_config

    port = int(get_config(name="app_port"))
    cert_file = get_config(name="cert")
    key_file = get_config(name="cert_key")
    init_ssl(cert_file=cert_file, key_file=key_file)
    if bool(int(get_config(name="debug"))) == True:
        log_level_std = "TRACE"
    else:
        log_level_std = "INFO"
    init_log(log_level_std=log_level_std)
else:
    port = 7000
    init_ssl()
    cert_file = "ssl.pem"
    key_file = "key.pem"

if __name__ == "__main__":
    try:
        logger.success(f"Сервер запущен на порту {port}")
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=port,
            ssl_certfile=f"{cert_folder_path}/{cert_file}",
            ssl_keyfile=f"{cert_folder_path}/{key_file}",
        )
    except Exception as err:
        logger.error(f"Ошибка запуски сервера: {err}")
    finally:
        logger.info("Сервер остановлен")
