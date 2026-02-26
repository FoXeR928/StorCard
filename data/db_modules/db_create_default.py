from sqlalchemy import select, delete, func
from loguru import logger
import secrets

from data.db_modules.db_create import Users, Configs, session_create


def create_default_users(
    recreate: bool = False,
    admin_login: str = "admin",
    admin_password: str = "admin",
    admin_name: str = "админ",
    is_admin: bool = True,
):
    with session_create() as session:
        try:
            if recreate:
                session.delete(Users)
                session.flush()
                logger.info("Удалены строки таблицы Users")
            exists_admin = session.scalar(
                select(Users).where(Users.is_admin == True).limit(1)
            )
            logger.trace("Проверенно существование записей в базе Users")
            if not exists_admin:
                admin = Users(
                    login=admin_login, user_name=admin_name, is_admin=is_admin
                )
                admin.set_password(admin_password)
                session.add(admin)
                session.commit()
                logger.success(f"Создан пользователь {admin_login} в базе Users")
            logger.trace("База пользователей настроена")
        except Exception as err:
            session.rollback()
            logger.error(f"Критическая ошибка при настройке пользователей : {err}")


def create_default_config(recreate: bool = False, **kwargs):
    defaults = {
        "app_port": ("Порт приложения", kwargs.get("app_port", 7000), "number"),
        "skey": ("Ключ OAuth2", kwargs.get("token", secrets.token_hex(64)), "generate"),
        "debug": ("Подробное логирование", str(kwargs.get("debug", False)), "boolean"),
        "front": ("Наличие web интерфейса", str(kwargs.get("front", True)), "boolean"),
        "cert": ("Файл сертификат", kwargs.get("cert", "ssl.pem"), "file"),
        "cert_key": (
            "Файл ключ сертификата",
            kwargs.get("cert_key", "key.pem"),
            "file",
        ),
        "short_token": (
            "Короткий токен (сек)",
            str(kwargs.get("short_token", 1800)),
            "number",
        ),
        "long_token": (
            "Длинный токен (сек)",
            str(kwargs.get("long_token", 604800)),
            "number",
        ),
    }
    with session_create() as session:
        try:
            if recreate:
                session.delete(Configs)
                session.flush()
                logger.info("Удалены строки таблицы Configs")
            existing_configs = session.scalars(select(Configs.name)).all()
            to_add = [
                Configs(name=k, about=v[0], value=str(v[1]), input_format=v[2])
                for k, v in defaults.items()
                if k not in existing_configs
            ]
            if to_add:
                session.add_all(to_add)
                session.commit()
                logger.success(f"Добавлено новых конфигов: {len(to_add)}")
            logger.trace("База конфигов настроена")
        except Exception as err:
            session.rollback()
            logger.error(f"Критическая ошибка при настройке конфигов: {err}")
            exit()
