from sqlalchemy import update, case
from loguru import logger

from data.config_modules.config_check import config_create
from data.db_modules.db_create import init_db
from data.db_modules.db_create import Configs, session_create
from data.db_modules.db_create_default import (
    create_default_users,
    create_default_config,
)


def create_config_app_start_query(**kwargs):
    app_port = kwargs.pop("app_port", 7000)
    front = kwargs.pop("front", True)
    config_create(data=kwargs)
    init_db()
    create_default_users()
    create_default_config()
    try:
        with session_create() as session:
            query = (
                update(Configs)
                .where(Configs.name == "app_port")
                .values(
                    value=case(
                        (Configs.name == "app_port", str(app_port)),
                        (Configs.name == "front", str(app_port)),
                    )
                )
            )
            session.execute(query)
            session.commit()
        logger.success(f"Port and Front status write in base")
        result = {
            "result": True,
            "message": "Конфинурационный файл и база созданы",
            "category": "success",
            "cod": 200,
        }
    except Exception as err:
        logger.error(f"Failed write port in base. Error: {err}")
        result = {
            "result": False,
            "message": "Failed write port in base.",
            "category": "error",
            "cod": 500,
        }
    return result
