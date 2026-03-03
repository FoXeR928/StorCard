import uvicorn
from loguru import logger
import src.core.config as config
import src.database.engine as engine
import src.core.certificate as certificate
import src.core.log as log
import src.core.system as system
from src.core.constants import CERTIFICATE_DIR
from src.database.repository.repo_default import (
    create_default_users,
    create_default_config,
)


def start_app():
    port = 7000
    log_level = "INFO"
    cert_file, key_file = "ssl.pem", "key.pem"
    if config.check_config():
        try:
            engine.init_db()
            create_default_config()
            create_default_users()

            from src.database.repository.repo_config import get_all_configs_dict
            conf = get_all_configs_dict()

            port = int(conf.get("app_port", 7000))
            cert_file = conf.get("cert", cert_file)
            key_file = conf.get("cert_key", key_file)
            if str(conf.get("debug")).lower() in ("true", "1"):
                log_level = "TRACE"
            log.init_log(log_level_std=log_level)
            certificate.init_ssl(cert_file=cert_file, key_file=key_file)
            logger.info("Конфигурация загружена из БД")
        except Exception as e:
            logger.error(f"Ошибка загрузки конфига из БД: {e}. Используем дефолты.")
    else:
        certificate.init_ssl()
        logger.warning("Файл конфигурации не найден, запуск в режиме установки")

    try:
        logger.success(f"Сервер запускается на 0.0.0.0:{port} (Log: {log_level})")
        uvicorn.run(
            app="src.api.app:app",
            host="0.0.0.0",
            port=port,
            ssl_certfile=CERTIFICATE_DIR / cert_file,
            ssl_keyfile=CERTIFICATE_DIR / key_file,
            log_level=log_level.lower(),
        )
    except Exception as err:
        logger.error(f"Ошибка Uvicorn: {err}")
    finally:
        logger.info("Работа сервера завершена")


if __name__ == "__main__":
    try:
        start_app()
    except Exception as err:
        logger.error(f"Критическая ошибка сервера: {err}")
        system.stop_server(1)
