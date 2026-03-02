from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from loguru import logger

from data.db_modules.db_query_config import get_config_token, get_config


def create_access_token(login: str, expires_use: bool) -> str:
    try:
        token_config = get_config_token()
        config_key = "long_token" if expires_use else "short_token"
        duration = int(token_config.get(key, 1800))
        now = datetime.now(timezone.utc)
        expire = datetime.now(timezone.utc) + timedelta(seconds=duration)
        payload = {
            "sub": login,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
        }
        return jwt.encode(payload, token_config.get("skey"), algorithm="HS256")
    except Exception as e:
        logger.error(f"Ошибка при создании токена для {login}: {e}")
        return ""


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, get_config("skey"), algorithms=["HS256"], leeway=10)
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except Exception as err:
        logger.error(f"Непредвиденная ошибка декодирования: {e}")
        return None
