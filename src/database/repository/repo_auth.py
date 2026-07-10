import jwt
from sqlalchemy import select
from loguru import logger
from fastapi import Depends, HTTPException, Request
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from src.database.models.model_users import Users
from src.database.db_engine import SessionLocal
from src.web.resources.responses import api_response, error_401, error_500


class OAuth2CookieStack(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        header_auth = request.headers.get("Authorization")
        if header_auth:
            return await super().__call__(request)
        return request.cookies.get("token")


oauth2_scheme = OAuth2CookieStack(tokenUrl="/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(401, "Not authenticated")

    try:
        conf = get_all_configs_dict()
        skey = conf.get("skey")
        payload = jwt.decode(token, skey, algorithms=["HS256"], leeway=10)
        login=payload.get("sub")
    except Exception as err:
        logger.error(f"Непредвиденная ошибка декодирования: {err}")
        loin=None
    if not login:
        raise HTTPException(401, "Token invalid or expired")
    user = get_user_by_login(login)
    if not user:
        raise HTTPException(404, "User not found")
    return user

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
                skey = get_all_configs_dict().get("skey")
                config_key = "long_token" if expires_use else "short_token"
                duration = int(conf.get(config_key, 3600))
                skey = conf.get("skey")
                if not skey:
                    logger.error("Критическая ошибка: 'skey' не найден в конфигах")
                    token=None
                now = datetime.now(timezone.utc)
                expire = datetime.now(timezone.utc) + timedelta(seconds=duration)
                payload = {
                    "sub": login,
                    "exp": int(expire.timestamp()),
                    "iat": int(now.timestamp()),
                }
                token=jwt.encode(payload, skey, algorithm="HS256")
            except Exception as e:
                logger.error(f"Ошибка при создании токена для {login}: {e}")
                token=None
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
