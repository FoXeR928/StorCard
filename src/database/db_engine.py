from os import getenv
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from loguru import logger
from src.core.mg_system import system
from src.database.models.model_default import Base
from src.database.repository.repo_default import (
    create_default_users,
    create_default_config,
)

SessionLocal = sessionmaker()


def init_db():
    try:
        driver = getenv("SQL_DRIVER", "sqlite")
        db_name=getenv("SQL_DB", "storcard_db")
        if driver == "sqlite":
            Path("./data/db").mkdir(exist_ok=True, parents=True)
            url = f"sqlite:///./data/db/{db_name}.db"
        elif driver in ["mysql", "postgresql"]:
            dialect = "mysql+pymysql" if driver == "mysql" else "postgresql+psycopg2"
            url = URL.create(
                drivername=dialect,
                username=getenv("SQL_USER"),
                password=getenv("SQL_PASSWORD"),
                host=getenv("SQL_HOST"),
                port=getenv("SQL_PORT"),
                database=db_name,
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
        create_default_config()
        create_default_users()
        return engine
    except Exception as err:
        logger.critical(f"Не удалось инициализировать базу данных Ошибка: {err}")
        system.stop_server(1)
