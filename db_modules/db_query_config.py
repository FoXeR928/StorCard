from sqlalchemy import select, update
import json
import os
from loguru import logger

from db_modules.db_create import Configs, session_create

def check_config(name: str):
    session = session_create()
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


def create_config_app_start_query(
    app_port:int=7000,
    sql_driver:str="sqlite",
    sql_host:str=None,
    sql_port:int=None,
    sql_db:str='ragi_db',
    sql_user:str=None,
    sql_password:str=None,
    db_path:str='instance'
):
    try:
        data={
            "sql_driver":sql_driver,
            "sql_host":sql_host,
            "sql_port":sql_port,
            "sql_db":sql_db,
            "sql_user":sql_user,
            "sql_password":sql_password,
            "db_path":db_path
        }
        if os.path.exists("instance")==False:
            os.mkdir('instance')
        with open("instance/config.json", "w") as file_config:
            json.dump(data, file_config, indent=4)
        result = {
            "result": True,
            "message": "\u0421\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0439 \u043a\u043e\u043d\u0444\u0438\u0433 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u0437\u0430\u0434\u0430\u043d",
            "category": "success",
            "cod": 200,
        }
        from db_modules.db_create_default import (
            create_default_users,
            create_default_config,
        )
        create_default_users()
        create_default_config()
        session = session_create()
        session.execute(
            update(Configs)
            .where(Configs.name == "app_port")
            .values(value=app_port)
        )
        session.commit()
        session.close()
        logger.success(f"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u044b \u0432 \u0431\u0430\u0437\u0443 \u043a\u043e\u043d\u0444\u0438\u0433\u0438 \u0434\u043b\u044f \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f")
    except Exception as err:
        logger.error(f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u0434\u0430\u0442\u044c \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0435 \u043a\u043e\u043d\u0444\u0438\u0433\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u041e\u0448\u0438\u0431\u043a\u0430 {err}")
        result = {
            "result": False,
            "message": "\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0439 \u043a\u043e\u043d\u0444\u0438\u0433 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435 \u0437\u0430\u0434\u0430\u043d",
            "category": "error",
            "cod": 500,
        }
    return result


def get_configs_query():
    session = session_create()
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
        session = session_create()
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
    session = session_create()
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