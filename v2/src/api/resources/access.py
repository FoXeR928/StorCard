from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt
from loguru import logger
from src.database.repository.repo_config import get_all_configs_dict
from src.database.repository.repo_auth import get_user_by_login

def create_access_token(login: str, expires_use: bool) -> str:
    try:
        conf = get_all_configs_dict()
        config_key = "long_token" if expires_use else "short_token"
        duration = int(conf.get(config_key, 3600))
        skey = conf.get("skey")
        if not skey:
            logger.error("Критическая ошибка: 'skey' не найден в конфигах")
            return ""
        now = datetime.now(timezone.utc)
        expire = datetime.now(timezone.utc) + timedelta(seconds=duration)
        payload = {
            "sub": login,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
        }
        return jwt.encode(payload, skey, algorithm="HS256")
    except Exception as e:
        logger.error(f"Ошибка при создании токена для {login}: {e}")
        return ""


def decode_access_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        conf = get_all_configs_dict()
        skey = conf.get("skey")
        payload = jwt.decode(token, skey, algorithms=["HS256"], leeway=10)
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except Exception as err:
        logger.error(f"Непредвиденная ошибка декодирования: {err}")
        return None

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

    login = decode_access_token(token)
    if not login:
        raise HTTPException(401, "Token invalid or expired")

    user = get_user_by_login(login)
    if not user:
        raise HTTPException(404, "User not found")
    return user
