import os
import secrets
import uuid
from datetime import datetime
from pathlib import Path

import bcrypt
from loguru import logger
from sqlalchemy import (
    ForeignKey,
    create_engine,
    func,
    DateTime,
    String,
    Boolean,
    event,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DOCKER_DB_URL = os.getenv("DATABASE_URL")

if DOCKER_DB_URL:
    DATABASE_URL = DOCKER_DB_URL
    connect_args = {}
    logger.info("Подключение к внешней СУБД из Docker Environment.")
else:
    DATA_DIR = Path("./data")
    DATABASE_URL = f"sqlite+aiosqlite:///{DATA_DIR / 'storcard.db'}"
    connect_args = {"check_same_thread": False}
    logger.info("DATABASE_URL не задана. Использование локальной SQLite.")

engine = create_async_engine(DATABASE_URL, connect_args=connect_args)

session_create = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):
    """SQLite по умолчанию не проверяет внешние ключи — включаем вручную."""
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


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
        nullable=False,
    )

    date_create: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    date_update: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
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
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class Cards(Base, ModelTemplate):
    __tablename__ = "cards"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    about: Mapped[str] = mapped_column(String(255), nullable=True)
    barcode: Mapped[str] = mapped_column(String(100), nullable=False)

    image_path: Mapped[str] = mapped_column(String(255), nullable=True)


class CardsAccess(Base, ModelTemplate):
    __tablename__ = "cards_access"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[str] = mapped_column(
        ForeignKey("cards.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False
    )

    access_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="viewer"
    )


async def ensure_default_admin() -> None:
    """
    Идемпотентно создаёт администратора, если его нет в БД.
    Вызывается из lifespan при старте и из тестов после create_all.
    """
    admin_login = os.getenv("ADMIN_LOGIN", "admin")

    async with session_create() as session:
        existing = (
            await session.scalars(select(Users).where(Users.login == admin_login))
        ).one_or_none()
        if existing:
            return

        admin_name = os.getenv("ADMIN_NAME", "Администратор")
        admin_password = os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(9)

        admin = Users(
            login=admin_login,
            user_name=admin_name,
            is_admin=True,
            disabled=False,
        )
        admin.set_password(admin_password)
        session.add(admin)
        await session.commit()

        logger.success(
            f"\n=========================================================\n"
            f" База данных успешно инициализирована!\n"
            f" Логин администратора: {admin_login}\n"
            f" Пароль администратора: {admin_password}\n"
            f"========================================================="
        )
