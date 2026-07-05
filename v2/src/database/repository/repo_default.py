from sqlalchemy import select, delete, func
from loguru import logger
import secrets
import src.database.engine as engine
from src.database.models.model_users import Users
from src.database.models.model_configs import Configs
import src.core.system as system


def create_default_users(recreate: bool = False, **kwargs):
    login = kwargs.get("admin_login", "admin")
    with engine.SessionLocal() as session:
        try:
            if recreate:
                session.execute(delete(Users))
                logger.warning("Таблица Users очищена")
            exists_admin = session.scalar(select(Users).where(Users.is_admin == True))
            logger.trace("Проверенно существование записей в базе Users")
            if not exists_admin:
                admin = Users(
                    login=login,
                    user_name=kwargs.get("admin_name", "админ"),
                    is_admin=True,
                )
                admin.set_password(kwargs.get("admin_password", "admin"))
                session.add(admin)
                session.commit()
                logger.success(f"Создан дефолтный админ: {login}")
        except Exception as err:
            session.rollback()
            logger.error(f"Критическая ошибка при настройке пользователей : {err}")


def create_default_config(recreate: bool = False, **kwargs):
    defaults = {
        "install_page": (
            "Стартовая страница",
            str(kwargs.get("install_page", False)),
            "boolean",
        ),
        "app_port": ("Порт приложения", kwargs.get("app_port", 7000), "number"),
        "skey": ("Ключ OAuth2", kwargs.get("token", secrets.token_hex(64)), "generate"),
        "debug": ("Подробное логирование", str(kwargs.get("debug", False)), "boolean"),
        "front_status": (
            "Наличие web интерфейса",
            str(kwargs.get("front", True)),
            "boolean",
        ),
        "cert": ("Файл сертификат", kwargs.get("cert", "ssl.pem"), "file"),
        "cert_key": (
            "Файл ключ сертификата",
            kwargs.get("cert_key", "key.pem"),
            "file",
        ),
        "short_token": (
            "Короткий токен (сек)",
            str(kwargs.get("short_token", 3600)),
            "number",
        ),
        "long_token": (
            "Длинный токен (сек)",
            str(kwargs.get("long_token", 604800)),
            "number",
        ),
    }
    with engine.SessionLocal() as session:
        try:
            if recreate:
                session.execute(delete(Configs))
                logger.warning("Таблица Configs очищена")
            existing_configs = session.scalars(select(Configs.name)).all()
            new_configs = [
                Configs(name=k, about=v[0], value=str(v[1]), input_format=v[2])
                for k, v in defaults.items()
                if k not in existing_configs
            ]
            if new_configs:
                session.add_all(new_configs)
                session.commit()
                logger.success(f"Добавлено настроек: {len(new_configs)}")
            logger.trace("База конфигов настроена")
        except Exception as err:
            session.rollback()
            logger.critical(f"Критическая ошибка при настройке конфигов: {err}")
            system.stop_server(1)
