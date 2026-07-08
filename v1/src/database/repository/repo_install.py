from sqlalchemy import update, case
from loguru import logger
import src.core.config as config
import src.database.engine as engine
from src.database.repository.repo_default import (
    create_default_users,
    create_default_config,
)
from src.database.models.model_configs import Configs
from src.core.responses import api_response, error_500


def install_db(**kwargs):
    app_port = kwargs.pop("app_port", 7000)
    front_status = kwargs.pop("front", True)
    if not config.config_create(data=kwargs):
        return error_500(
            "Возникла ошибка при создание конфигурационного файла. Проверьти логи"
        )
    engine.init_db()
    create_default_users()
    create_default_config()
    settings = {"app_port": app_port, "front_status": front_status}
    with engine.SessionLocal() as session:
        try:
            for name, val in settings.items():
                session.execute(
                    update(Configs).where(Configs.name == name).values(value=val)
                )
            session.commit()
            logger.success("Конфигурация порта и статуса web интерфейса записаны в БД")
            return api_response(
                True, "Конфигурационный файл и база успешно созданы", 201
            )
        except Exception as err:
            logger.error(f"Ошибка записи настроек. Error: {err}")
            return error_500(f"Не удалось записать настройки: {err}")
