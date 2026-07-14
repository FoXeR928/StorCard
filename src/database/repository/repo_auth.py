import jwt
from sqlalchemy import select
from loguru import logger
from datetime import datetime, timedelta, timezone
from database.models.model_users import Users
from database.db_connect import SessionLocal
from web.resources.responses import api_response, error_401, error_500


def get_user_by_login(login: str):
    with SessionLocal() as session:
        return (
            session.execute(
                select(Users.login, Users.user_name, Users.is_admin).where(
                    Users.login == login
                )
            )
            .mappings()
            .one_or_none()
        )


def authenticate_user(login: str, password: str, long_session: bool):
    try:
        with SessionLocal() as session:
            user = session.scalars(
                select(Users).where(Users.login == login)
            ).one_or_none()
            if not user or not user.check_password(password):
                error_401()
            try:
                skey = get_config_val("skey")
                config_key = "long_token" if long_session else "short_token"
                duration = int(get_config_val(config_key))
                if not skey:
                    logger.error("Критическая ошибка: 'skey' не найден в конфигах")
                    token = None
                now = datetime.now(timezone.utc)
                expire = datetime.now(timezone.utc) + timedelta(seconds=duration)
                payload = {
                    "sub": login,
                    "exp": int(expire.timestamp()),
                    "iat": int(now.timestamp()),
                }
                token = jwt.encode(payload, skey, algorithm="HS256")
            except Exception as e:
                logger.error(f"Ошибка при создании токена для {login}: {e}")
                token = None
            if not token:
                return error_500("Ошибка генерации ключа доступа")
            return api_response(
                success=True,
                message="Авторизация прошла успешно",
                code=200,
                access_token=token,
                token_type="bearer",
            )
    except Exception as e:
        logger.error(f"Системная ошибка при аутентификации {login}: {e}")
        return error_500("Внутренняя ошибка сервера")
