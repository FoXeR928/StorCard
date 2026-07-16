import jwt
from sqlalchemy import select
from loguru import logger
from datetime import datetime, timedelta, timezone
from database.models.model_users import Users
from database.db_connect import AsyncSessionLocal
from web.resources.responses import api_response, error_401, error_500
from core.core_config import REFRESH_TOKEN, ACCESS_TOKEN, SECRET_KEY


async def get_user_by_login(login: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Users.login, Users.user_name, Users.is_admin).where(
                Users.login == login
            )
        )
        return result.mappings().one_or_none()


async def authenticate_user(login: str, password: str, long_session: bool):
    try:
        async with AsyncSessionLocal() as session:
            user_query = await session.execute(
                select(Users).where(Users.login == login)
            )
            user = user_query.scalars().one_or_none()
            if not user or not user.check_password(password):
                return error_401()
            if long_session:
                duration = REFRESH_TOKEN
            else:
                duration = ACCESS_TOKEN
            try:
                now = datetime.now(timezone.utc)
                expire = datetime.now(timezone.utc) + timedelta(seconds=duration)
                payload = {
                    "sub": login,
                    "exp": int(expire.timestamp()),
                    "iat": int(now.timestamp()),
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
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
