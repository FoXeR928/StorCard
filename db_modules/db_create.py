from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, Session
from sqlalchemy import ForeignKey, create_engine, func, DateTime
from datetime import datetime
import secrets
import bcrypt
from loguru import logger

from instance.config_read import init_confg

config = init_confg()


def init_db():
    try:
        engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])
        Base.metadata.create_all(engine)
        logger.info("\u0411\u0430\u0437\u0430 \u0434\u0430\u043d\u043d\u044b\u0445 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d\u0430")
        return engine
    except Exception as err:
        logger.critical(f"\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0431\u0430\u0437\u0443 \u0434\u0430\u043d\u043d\u044b\u0445 \u041e\u0448\u0438\u0431\u043a\u0430: {err}")
        exit()


def session_create():
    from api.api_app import engine

    session = Session(bind=engine)
    return session


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