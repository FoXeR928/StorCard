import os
import secrets
from datetime import datetime
import uuid
from pathlib import Path
import bcrypt
from loguru import logger
from sqlalchemy import ForeignKey, create_engine, func, DateTime, String, Boolean, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DOCKER_DB_URL = os.getenv("DATABASE_URL")

if DOCKER_DB_URL:
    DATABASE_URL = DOCKER_DB_URL
    connect_args = {}
    logger.info("Подключение к внешней СУБД из Docker Environment.")
else:
    DATA_DIR = Path("./data")
    DATABASE_URL = f"sqlite:///{DATA_DIR / 'storcard.db'}"
    connect_args = {"check_same_thread": False}
    logger.info("DATABASE_URL не задана. Использование локальной SQLite.")

engine = create_engine(DATABASE_URL, connect_args=connect_args)
session_create = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass


class ModelTemplate:
    """
    Абстрактный шаблон, содержащий общие поля для всех таблиц.
    Автоматически генерирует UUID и управляет временными метками.
    """
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()), 
        unique=True, 
        nullable=False
    )
    
    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        onupdate=func.now(), 
        nullable=True
    )

class Users(Base, ModelTemplate):
    __tablename__ = "users"

    login: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def set_password(self, password: str):
        generate_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.password_hash = generate_hash.decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash or self.disabled:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


class Cards(Base, ModelTemplate):
    __tablename__ = "cards"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    about: Mapped[str] = mapped_column(String(255), nullable=True)
    barcode: Mapped[str] = mapped_column(String(100), nullable=False)
    
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)


class CardsAccess(Base, ModelTemplate):
    __tablename__ = "cards_access"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    card_id: Mapped[str] = mapped_column(ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    
    access_level: Mapped[str] = mapped_column(String(20), nullable=False, default="viewer")

@event.listens_for(Users.__table__, "after_create")
def insert_default_admin(target, connection, **kw):
    admin_login = os.getenv("ADMIN_LOGIN", "admin")
    admin_name = os.getenv("ADMIN_NAME", "Администратор")
    admin_password = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(9)

    temp_admin = Users()
    temp_admin.set_password(admin_password)

    connection.execute(
        target.insert().values(
            id=str(uuid.uuid4()),
            login=admin_login,
            user_name=admin_name,
            password_hash=temp_admin.password_hash,
            is_admin=True,
            disabled=False
        )
    )

    logger.success(
        f"\n=========================================================\n"
        f" База данных успешно инициализирована!\n"
        f" Логин администратора: {admin_login}\n"
        f" Пароль администратора: {admin_password}\n"
        f"========================================================="
    )
