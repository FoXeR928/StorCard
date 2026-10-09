import os
import secrets
import jwt
from pathlib import Path
from datetime import datetime, timedelta, timezone
from loguru import logger
from fastapi import HTTPException, status
from sqlalchemy import select

from db.db_create import session_create, Users

SECRET_KEY_PATH=Path("./data/secret.key")

if os.path.exists(SECRET_KEY_PATH):
    with open(SECRET_KEY_PATH,'r') as f:
        SECRET_KEY=f.read().strip()
else:
    SECRET_KEY=secrets.token_urlsafe(64)
    with open(SECRET_KEY_PATH, "w") as f:
        f.write(SECRET_KEY)
    logger.info("JWT токен создан")

ALGORITHM = "HS256"

def create_token(data: dict, expires_use: bool = False) -> str:
    """Генерация OAuth2 Access Token"""
    try:
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=7) if expires_use else now + timedelta(minutes=30)
        
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Токен успешно создан для пользователя: {data.get('sub')}")
        return encoded_jwt
    except Exception as err:
        logger.error(f"Внутренняя ошибка при кодировании токена: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при генерации токена доступа."
        )


def decode_token(token: str) -> str | None:
    if not token:
        return None
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.debug("Срок действия JWT-токена истек.")
        return None
    except jwt.PyJWTError as err:
        logger.error(f"Ошибка валидации подписи JWT-токена: {err}")
        return None


def auth_user_query(login: str, password: str) -> dict:
    """
    Бизнес-логика проверки логина/пароля и выдачи токена.
    В случае ошибки нативно генерирует стандартные HTTPException.
    """
    with session_create() as session:
        user = session.scalars(select(Users).where(Users.login == login)).one_or_none()
        
        if user is None or user.disabled:
            logger.warning(f"Неудачная попытка входа: пользователь {login} не найден или заблокирован.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.check_password(password=password):
            logger.warning(f"Неудачная попытка входа: неверный пароль для пользователя {login}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token = create_token(data={"sub": user.login})
        logger.info(f"Пользователь {user.login} успешно авторизован в системе.")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "login": user.login,
                "user_name": user.user_name,
                "is_admin": user.is_admin
            }
        }
