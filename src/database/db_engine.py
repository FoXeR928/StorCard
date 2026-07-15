from os import getenv
from pathlib import Path
from sys import exit
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from loguru import logger
from core.core_config import DB_DRIVER, DB_NAME
from database.models.model_default import Base
from database.db_connect import SessionLocal
from database.repository.repo_users import create_default_users


def init_db():
    try:
        if DB_DRIVER == "sqlite":
            Path("./data/db").mkdir(exist_ok=True, parents=True)
            url = f"sqlite:///./data/db/{DB_NAME}.db"
        elif DB_DRIVER in ["mysql", "postgresql"]:
            driver = "mysql+pymysql" if DB_DRIVER == "mysql" else "postgresql+psycopg2"
            url = URL.create(
                drivername=driver,
                username=getenv("SQL_USER"),
                password=getenv("SQL_PASSWORD"),
                host=getenv("SQL_HOST"),
                port=getenv("SQL_PORT"),
                database=DB_NAME,
            )
        else:
            logger.critical(
                f"Не удалось инициализировать базу данных Ошибка: Недопустимы драйвер БД"
            )
            exit(1)
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        SessionLocal.configure(bind=engine)
        logger.success("База данных инициализирована")
        create_default_users()
        return engine
    except Exception as err:
        logger.critical(f"Не удалось инициализировать базу данных Ошибка: {err}")
        exit(1)
