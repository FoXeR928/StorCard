from sqlalchemy import select, delete, func
from loguru import logger
import secrets

from db_modules.db_create import Users, Configs, session_create


def create_default_users(
    recreate: bool = False,
    admin_login: str = "admin",
    admin_password: str = "admin",
    admin_name: str = "админ",
    is_admin: bool = True,
):
    session = session_create
    base = Users
    if recreate:
        try:
            session.execute(delete(base))
            session.commit()
            logger.info("Удалены строки таблицы Users")
        except Exception as err:
            logger.error(f"Не удалось удалить строки таблицы Users Ошибка {err}")
    try:
        check_admin = session.scalar(
            select(func.count(base.login)).where(base.is_admin == True)
        )
        logger.trace("Проверенно существование записей в базе Users")
    except Exception as err:
        logger.error(
            f"Не удалось проверить существование записей таблицы Users Ошибка {err}"
        )
    if check_admin == 0:
        try:
            admin = base(login=admin_login, user_name=admin_name, is_admin=is_admin)
            admin.set_password(admin_password)
            session.add(admin)
            session.commit()
            logger.debug(f"Создан запрос на добавление {admin_login} в базу Users")
        except Exception as err:
            logger.error(
                f"Не удалось создать запрос на добавление {admin_login} в базу Users Ошибка {err}"
            )
    else:
        logger.debug("Пользователи по умолчанию уже в базе есть")
    session.close()


def create_default_config(
    recreate: bool = False,
    app_port: int = 7000,
    token: str = secrets.token_hex(64),
    debug: bool = False,
):
    configs_list = (
        ("app_port", "Порт приложения", app_port, "number"),
        ("skey", "Ключ для генерации OAuth2 токена", token, "text"),
        ("debug", "Подробное логирование", debug, "boolen"),
    )
    session = session_create
    base = Configs
    if recreate:
        try:
            session.execute(delete(base))
            session.commit()
            logger.info("Удалены строки таблицы Configs")
        except Exception as err:
            logger.error(f"Не удалось удалить строки таблицы Configs Ошибка {err}")
    add_list = list()
    for configs in configs_list:
        try:
            check_config = session.scalars(
                select(base).where(base.name == configs[0])
            ).one_or_none()
            logger.trace(
                f"Проверенно существование записи {configs[0]} в таблице Configs"
            )
        except Exception as err:
            logger.error(
                f"Не удалось проверить существование записи {configs[0]} в таблице Configs Ошибка {err}"
            )
        if check_config == None:
            try:
                config = base(
                    name=configs[0],
                    about=configs[1],
                    value=configs[2],
                    input_format=configs[3],
                )
                add_list.append(config)
                logger.debug(f"Создан запрос на добавление конфига в базу Configs")
            except Exception as err:
                logger.error(
                    f"Не удалось создать запрос на добавление в базу Configs Ошибка {err}"
                )
    if len(add_list) != 0:
        try:
            session.add_all(add_list)
            session.commit()
            logger.info("Добавлены конфиги по умолчанию")
        except Exception as err:
            logger.error(
                f"Не удалось добавить конфиги по умолчанию в базу Configs Ошибка {err}"
            )
            exit()
    else:
        logger.debug("Конфиги по умолчанию уже в базе есть")
    session.close()
