from sqlalchemy import select, update
from datetime import datetime, timedelta
import jwt
from loguru import logger

from db_modules.db_create import Users, session_create
from db_modules.db_query import check_user
from db_modules.db_query_config import get_config


def create_token(data: dict, expires_use: bool = False):
    try:
        expire = datetime.utcnow()
        if expires_use == True:
            expire += timedelta(days=7)
        else:
            expire += timedelta(minutes=30)
        data["exp"] = expire
        encoded_jwt = jwt.encode(
            payload=data, key=get_config(name="skey"), algorithm="HS256"
        )
        result = encoded_jwt
        logger.debug(f"Токен создан для пользователя {data['sub']}")
    except Exception as err:
        logger.error(f"Ошибка сервера создания токена: {err}")
        raise False
    return result


def decode_token(token: str):
    if token!=None:
        try:
            payload = jwt.decode(jwt=token, key=get_config(name="skey"), algorithms="HS256")
            user = payload.get("sub")
        except jwt.ExpiredSignatureError:
            logger.debug("Signature has expired")
            user = None
        except Exception as err:
            logger.error(f"Ошибка сервера чтения токена: {err}")
            user = None
    else:
        user=None
    return user


def get_current_user_query(login: str):
    if check_user(login=login) == True:
        session = session_create
        try:
            user = session.execute(
                select(Users.login, Users.user_name, Users.is_admin).where(
                    Users.login == login
                )
            ).one_or_none()
            result = user
        except Exception as err:
            logger.error(
                f"Не удалось получить данные пользователя {login} Ошибка {err}"
            )
            result = None
        finally:
            session.close()
    else:
        result = None
    return result


def auth_query(login: str, password: str):
    result_no_auth = {
        "result": False,
        "message": "Неверный логин или пароль",
        "category": "warning",
        "cod": 401,
    }
    result_error = {
        "result": False,
        "message": "Ошибка сервера авторизация не удалась",
        "category": "error",
        "cod": 500,
    }
    if check_user(login=login) == True:
        session = session_create
        try:
            auth = session.scalars(select(Users).where(Users.login == login)).one()
            check_auth = auth.check_password(password=password)
            logger.debug(f"Авторизация пользователя {login} прошла успешно")
        except Exception as err:
            session.close()
            logger.error(f"Не удалось авторизировать пользователя {login} Ошибка {err}")
            raise result_error
        finally:
            session.close()
        if check_auth == True:
            token = create_token(data={"sub": login})
            if token != False:
                result = {
                    "result": True,
                    "access_token": token,
                    "token_type": "bearer",
                    "message": "Авторизация прошла успешно",
                    "category": "success",
                    "cod": 200,
                }
            else:
                result = result_error
        else:
            result = result_no_auth
    else:
        result = result_no_auth
    return result


def logout_query(login: str):
    session = session_create
    try:
        session.execute(update(Users).where(Users.login == login).values(token=None))
        session.commit()
        result = {
            "result": True,
            "message": "Пользователь деавторизирован",
            "category": "success",
            "cod": 201,
        }
        logger.debug(f"Пользователь {login} деавторизирован")
    except Exception as err:
        logger.error(f"Не удалось деавторизировать пользователя {login} Ошибка {err}")
        return {
            "result": False,
            "message": "Ошибка сервера деавторизация не удалась",
            "category": "error",
            "cod": 500,
        }
    finally:
        session.close()
    return result
