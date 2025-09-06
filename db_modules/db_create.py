from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session
from sqlalchemy import ForeignKey, create_engine, func, DateTime,BLOB
from datetime import datetime
import secrets
import bcrypt
import json
from loguru import logger

def init_confg():
    try:
        with open("./instance/config.json","r") as file_config:
            config = json.load(file_config)
        logger.info("\u0418\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d \u043a\u043e\u043d\u0444\u0438\u0433 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445")
        return config
    except Exception as err:
        logger.critical(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438 \u043a\u043e\u043d\u0444\u0438\u0433\u043e\u0432 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445: {err}")
        exit()


def init_db():
    try:
        config=init_confg()
        if config["sql_driver"]=="sqlite":
            sql_url=f"{config["sql_driver"]}:///{config["db_path"]}/{config["sql_db"]}.db"
        elif config["sql_driver"]=="mysql":
            sql_url=f"{config["sql_driver"]}://{config["sql_user"]}:{config["sql_password"]}@{config["sql_host"]}:{config["sql_port"]}/{config["sql_db"]}"
        elif config["sql_driver"]=="postgresql":
            sql_url=f"{config["sql_driver"]}://{config["sql_user"]}:{config["sql_password"]}@{config["sql_host"]}:{config["sql_port"]}/{config["sql_db"]}"
        else:
            raise None
        engine = create_engine(url=sql_url)
        Base.metadata.create_all(engine)
        session = Session(bind=engine)
        logger.info("База данных инициализирована")
        return session
    except Exception as err:
        logger.critical(f"Не удалось инициализировать базу данных Ошибка: {err}")
        exit()

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=True)
    user_name: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(nullable=False, default=False)
    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def set_password(self, password: str):
        generate_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.password_hash = generate_hash

    def check_password(self, password: str):
        check_password_func = bcrypt.checkpw(password.encode(), self.password_hash)
        check_active = self.disabled == False
        return check_password_func and check_active


class Configs(Base):
    __tablename__ = "configs"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    about: Mapped[str] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=False)
    input_format: Mapped[str] = mapped_column(nullable=False)
    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def generate_token(self):
        self.token = secrets.token_hex(64)

    def check_token(self, check_token):
        if self.token == check_token:
            return True
        else:
            return False
        

class Cards(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    about: Mapped[str] = mapped_column(nullable=True)
    own_login: Mapped[str] = mapped_column(ForeignKey(Users.login, onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    code: Mapped[int] = mapped_column(nullable=False)
    code_type: Mapped[str] = mapped_column(nullable=False)
    card_image:Mapped[str] = mapped_column(BLOB,nullable=True)
    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

class CardsAccess(Base):
    __tablename__ = "cards_access"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, nullable=False)
    user_login: Mapped[str] = mapped_column(ForeignKey(Users.login, onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    card_id: Mapped[int] = mapped_column(ForeignKey(Cards.id, onupdate="CASCADE",ondelete="CASCADE"),nullable=False)
    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=datetime.now()
    )
    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

session_create=init_db()