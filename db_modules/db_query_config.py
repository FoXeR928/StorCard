from sqlalchemy import select, update
from loguru import logger

from db_modules.db_create import Configs, session_create

def check_config(name: str):
    session = session_create
    try:
        config = session.scalars(select(Configs).where(Configs.name == name)).one_or_none()
        logger.trace(f"Проверка чата {name} в базе")
        if config != None:
            result = True
        else:
            result = False
        logger.debug(f"Проверка чата {name} в базе прошла успешно")
    except Exception as err:
        logger.error(f"Не удалось проверить чата {name} Ошибка {err}")
        result = False
    finally:
        session.close()
    return result


def get_configs_query():
    session = session_create
    try:
        search_config = session.execute(
            select(Configs.name, Configs.about, Configs.value, Configs.input_format)
        ).all()
        search_result = list()
        for config in search_config:
            search_result.append(
                {
                    "name": config.name,
                    "about": config.about,
                    "value": config.value,
                    "input_format": config.input_format,
                }
            )
        result = {
            "result": True,
            "configs_ai": search_result,
            "message": "Конфиги получены",
            "category": "success",
            "cod": 200,
        }
        logger.trace(f"Получен список конфигов из базы")
    except Exception as err:
        logger.error(f"Не удалось получить список конфигов из базы Ошибка {err}")
        return {
            "result": False,
            "message": "Ошибка сервера не удалось получить конфиги приложения",
            "category": "error",
            "cod": 500,
        }
    finally:
        session.close()
    return result


def update_config_query(name: str, value):
    if check_config(name=name)==True:
        session = session_create
        try:
            session.execute(update(Configs).where(Configs.name == name).values(value=value))
            session.commit()
            logger.success(f"Обноваление значения конфигова {name} на {value} из базы")
            result = {
                "result": True,
                "message": "Конфиг обнавлен",
                "category": "success",
                "cod": 200,
            }
        except Exception as err:
            logger.error(f"Не удалось обновить значения конфигова {name} Ошибка {err}")
            result = {
                "result": False,
                "message": "Ошибка сервера конфиг не обнавлен",
                "category": "error",
                "cod": 500,
            }
        finally:
            session.close()
    else:
        result = {
            "result": False,
            "message": "Не найден конфиг",
            "category": "warning",
            "cod": 404,
        }
    return result

def get_config(name: str):
    session = session_create
    try:
        search_config = session.scalars(
            select(Configs.value).where(Configs.name == name)
        ).first()
        result = search_config
        logger.trace(f"Получено значения конфигова {name} из базы")
    except Exception as err:
        logger.error(
            f"Не удалось получить значения конфигова {name} из базы Ошибка {err}"
        )
        result = None
    finally:
        session.close()
    return result