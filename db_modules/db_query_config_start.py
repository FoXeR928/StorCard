from sqlalchemy import update
import json
import os
from loguru import logger


def create_config_app_start_query(
    app_port: int = 7000,
    sql_driver: str = "sqlite",
    sql_host: str = None,
    sql_port: int = None,
    sql_db: str = "ragi_db",
    sql_user: str = None,
    sql_password: str = None,
    db_path: str = "instance",
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
        if os.path.exists("instance") == False:
            os.mkdir("instance")
        with open("instance/config.json", "w") as file_config:
            json.dump(data, file_config, indent=4)
        result = {
            "result": True,
            "message": "\u0421\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0439 \u043a\u043e\u043d\u0444\u0438\u0433 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u0437\u0430\u0434\u0430\u043d",
            "category": "success",
            "cod": 200,
        }
        from db_modules.db_create import Configs, session_create
        from db_modules.db_create_default import (
            create_default_users,
            create_default_config,
        )

        create_default_users()
        create_default_config()
        session = session_create
        session.execute(
            update(Configs).where(Configs.name == "app_port").values(value=app_port)
        )
        session.commit()
        session.close()
        logger.success(
            f"\u0414\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u044b \u0432 \u0431\u0430\u0437\u0443 \u043a\u043e\u043d\u0444\u0438\u0433\u0438 \u0434\u043b\u044f \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f"
        )
    except Exception as err:
        logger.error(
            f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0437\u0430\u0434\u0430\u0442\u044c \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0435 \u043a\u043e\u043d\u0444\u0438\u0433\u0438 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u041e\u0448\u0438\u0431\u043a\u0430 {err}"
        )
        result = {
            "result": False,
            "message": "\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0439 \u043a\u043e\u043d\u0444\u0438\u0433 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f \u043d\u0435 \u0437\u0430\u0434\u0430\u043d",
            "category": "error",
            "cod": 500,
        }
    return result
