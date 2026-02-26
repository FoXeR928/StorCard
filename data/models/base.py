from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session, sessionmaker
from sqlalchemy import ForeignKey, create_engine, func, DateTime, BLOB, UUID
from datetime import datetime
import secrets
import bcrypt
import sys
import uuid
from loguru import logger

from data.config_modules.config_init import init_confg

session_create = sessionmaker()


def init_db():
    try:
        config = init_confg()
        if config["sql_driver"] == "sqlite":
            sql_url = (
                f"{config["sql_driver"]}:///{config["db_path"]}/{config["sql_db"]}.db"
            )
        elif config["sql_driver"] == "mysql":
            sql_url = f"{config["sql_driver"]}://{config["sql_user"]}:{config["sql_password"]}@{config["sql_host"]}:{config["sql_port"]}/{config["sql_db"]}"
        elif config["sql_driver"] == "postgresql":
            sql_url = f"{config["sql_driver"]}://{config["sql_user"]}:{config["sql_password"]}@{config["sql_host"]}:{config["sql_port"]}/{config["sql_db"]}"
        else:
            raise None
        engine = create_engine(sql_url, pool_pre_ping=True)
        Base.metadata.create_all(engine)
        session_create.configure(bind=engine)
        logger.info("База данных инициализирована")
        return engine
    except Exception as err:
        logger.critical(f"Не удалось инициализировать базу данных Ошибка: {err}")
        sys.exit(1)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    date_create: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )


class Users(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    user_name: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)

    def set_password(self, password: str):
        salt=bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode(), salt)

    def check_password(self, password: str) -> bool:
        if self.disabled or not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode(), self.password_hash)


class Configs(Base, TimestampMixin):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    about: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    input_format: Mapped[str] = mapped_column(nullable=False, default="text")

    def generate_token(self):
        self.token = secrets.token_hex(64)

    def check_token(self, check_token):
        if self.token == check_token:
            return True
        else:
            return False


class Cards(Base, TimestampMixin):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, unique=True, default=uuid.uuid4, nullable=False
    )
    name: Mapped[str] = mapped_column(nullable=False)
    about: Mapped[str] = mapped_column(nullable=True)
    own_login: Mapped[str] = mapped_column(
        ForeignKey(Users.login, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    image: Mapped[str] = mapped_column(BLOB, nullable=True)
    version: Mapped[int] = mapped_column(default=1)
    code: Mapped[str] = mapped_column(nullable=False)
    code_type: Mapped[str] = mapped_column(nullable=False)


class CardsAccess(Base, TimestampMixin):
    __tablename__ = "cards_access"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    user_login: Mapped[str] = mapped_column(
        ForeignKey(Users.login, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(
        ForeignKey(Cards.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
