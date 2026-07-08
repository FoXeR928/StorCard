from os import getenv
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from loguru import logger
import src.core.system as system
from src.database.base import Base

SessionLocal = sessionmaker()


def init_db():
    try:
        driver = os.getenv("SQL_DRIVER", "sqlite")
        if driver == "sqlite":
            Path("./data/db").mkdir(exist_ok=True, parents=True)
            url = f"sqlite:///./data/db/base.db"
        elif driver in ["mysql", "postgresql"]:

            dialect = "mysql+pymysql" if driver == "mysql" else "postgresql+psycopg2"
            url = URL.create(
                drivername=dialect,
                username=conf["sql_user"],
                password=conf["sql_password"],
                host=conf["sql_host"],
                port=conf["sql_port"],
                database=conf["sql_db"],
            )
        else:
            logger.critical(
                f"Не удалось инициализировать базу данных Ошибка: Недопустимы драйвер БД"
            )
            system.stop_server(1)
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        SessionLocal.configure(bind=engine)
        logger.success("База данных инициализирована")
        return engine
    except Exception as err:
        logger.critical(f"Не удалось инициализировать базу данных Ошибка: {err}")
        system.stop_server(1)
