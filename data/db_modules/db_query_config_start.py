from sqlalchemy import update
from loguru import logger

from data.config_modules.config_check import config_create


def create_config_app_start_query(
    app_port: int = 7000,
    sql_driver: str = "sqlite",
    sql_host: str = None,
    sql_port: int = None,
    sql_db: str = "ragi_db",
    sql_user: str = None,
    sql_password: str = None,
    db_path: str = "instance",
    front: bool = True,
):
    try:
        data = {
            "sql_driver": sql_driver,
            "sql_host": sql_host,
            "sql_port": sql_port,
            "sql_db": sql_db,
            "sql_user": sql_user,
            "sql_password": sql_password,
            "db_path": db_path,
        }
        config_create(data=data)
        from data.db_modules.db_create import Configs, session_create
        from data.db_modules.db_create_default import (
            create_default_users,
            create_default_config,
        )

        create_default_users()
        create_default_config()
        session = session_create
        session.execute(
            update(Configs).where(Configs.name == "app_port").values(value=app_port)
        )
        session.execute(
            update(Configs).where(Configs.name == "front").values(value=front)
        )
        session.commit()
        session.close()
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
