from functools import lru_cache
from loguru import logger
from sqlalchemy import select, update
import src.database.engine as engine
from src.database.models.model_configs import Configs
from src.core.responses import api_response, error_404


@lru_cache(maxsize=1)
def get_all_configs_dict():
    with engine.SessionLocal() as session:
        rows = session.execute(select(Configs.name, Configs.value)).all()
        return {row.name: row.value for row in rows}


def get_config_val(name: str, default=None):
    return get_all_configs_dict().get(name, default)


def update_config_query(name: str, value: str):
    with engine.SessionLocal() as session:
        try:
            result = session.execute(
                update(Configs).where(Configs.name == name).values(value=str(value))
            )
            if result.rowcount == 0:
                return api_response(False, "Конфиг не найден", 404)
            session.commit()
            get_all_configs_dict.cache_clear()
            return api_response(True, f"Конфиг {name} обновлен")
        except Exception:
            session.rollback()
            return api_response(False, "Ошибка БД", 500)


def get_configs_list_api():
    with engine.SessionLocal() as session:
        try:
            configs = (
                session.execute(
                    select(
                        Configs.name, Configs.about, Configs.value, Configs.input_format
                    )
                )
                .mappings()
                .all()
            )
            return api_response(
                True, "Список конфигураций получен", 200, configs=list(configs)
            )
        except Exception as err:
            logger.error(f"Ошибка получения конфигов: {err}")
            return api_response(False, "Ошибка сервера при чтении настроек", 500)


"""Проверено"""
