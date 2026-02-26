from sqlalchemy import select, update
from loguru import logger

from data.db_modules.db_create import Configs, session_create

def check_config(name: str) -> bool:
    with session_create() as session:
        try:
            return session.scalar(select(Configs.id).where(Configs.name == name).exists().select())
        except Exception as err:
            logger.error(f"Ошибка при проверке конфига {name}: {err}")
            return False

def get_configs_query():
    with session_create() as session:
        try:
            configs = session.execute(
                select(Configs.name, Configs.about, Configs.value, Configs.input_format)
            ).mappings().all()
            return {
                "result": True,
                "configs_ai": configs,
                "message": "Конфиги получены",
                "category": "success",
                "cod": 200,
            }
        except Exception as err:
            logger.error(f"Ошибка получения списка конфигов: {err}")
            return {
                "result": False,
                "message": "Ошибка сервера при получении конфигов",
                "category": "error",
                "cod": 500,
            }

def update_config_query(name: str, value):
    with session_create() as session:
        try:
            result = session.execute(
                update(Configs).where(Configs.name == name).values(value=str(value))
            )
            session.commit()
            if result.rowcount == 0:
                return {
                    "result": False,
                    "message": "Конфиг не найден",
                    "category": "warning",
                    "cod": 404,
                }

            logger.success(f"Конфиг {name} обновлен на {value}")
            return {
                "result": True,
                "message": "Конфиг обновлен",
                "category": "success",
                "cod": 200,
            }
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка обновления конфига {name}: {err}")
            return {
                "result": False,
                "message": "Ошибка сервера при обновлении",
                "category": "error",
                "cod": 500,
            }

def get_config(name: str):
    with session_create() as session:
        try:
            value = session.scalar(select(Configs.value).where(Configs.name == name))
            logger.trace(f"Получено значение конфига {name}")
            return value
        except Exception as err:
            logger.error(f"Ошибка получения конфига {name}: {err}")
            return None

def get_all_configs():
    with session_create() as session:
        try:
            rows = session.execute(select(Configs.name, Configs.value)).all()
            logger.trace("Все конфиги загружены для старта")
            return {row.name: row.value for row in rows}
        except Exception as err:
            logger.error(f"Ошибка загрузки всех конфигов: {err}")
            return {}