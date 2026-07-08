from sqlalchemy import update, case
from loguru import logger
from src.database.db_engine import engine
from src.database.models.model_configs import Configs
from src.web.resources.responses import api_response, error_500


def install_db(**install_date):
    with engine.SessionLocal() as session:
        try:
            for name, val in install_date.items():
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
