import os
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from loguru import logger
from fastapi import HTTPException, status
from sqlalchemy import select

from db.db_create import session_create, Users
from core.config import SECRET_KEY_PATH

if os.path.exists(SECRET_KEY_PATH):
    with open(SECRET_KEY_PATH, "r") as f:
        SECRET_KEY = f.read().strip()
else:
    SECRET_KEY = secrets.token_urlsafe(64)
    with open(SECRET_KEY_PATH, "w") as f:
        f.write(SECRET_KEY)
    logger.info("JWT ключ создан")

ALGORITHM = "HS256"

# Сроки жизни токенов
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
REFRESH_TOKEN_DAYS = int(os.getenv("REFRESH_TOKEN_DAYS", "30"))


def create_token(data: dict, token_type: str = "access") -> str:
    """Генерация access или refresh токена."""
    try:
        now = datetime.now(timezone.utc)
        if token_type == "refresh":
            expire = now + timedelta(days=REFRESH_TOKEN_DAYS)
        else:
            expire = now + timedelta(minutes=ACCESS_TOKEN_MINUTES)

        to_encode = data.copy()
        to_encode.update({"exp": expire, "type": token_type})

        return jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    except Exception as err:
        logger.error(f"Ошибка кодирования токена: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при генерации токена.",
        )


def decode_token(token: str, expected_type: str = "access") -> str | None:
    """Возвращает sub (login) или None при любой ошибке/подмене типа."""
    if not token:
        return None
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            logger.debug(
                f"Отклонён токен: ожидался тип '{expected_type}', "
                f"получен '{payload.get('type')}'"
            )
            return None
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        logger.debug("JWT истёк.")
        return None
    except jwt.PyJWTError as err:
        logger.error(f"Ошибка валидации JWT: {err}")
        return None


async def auth_user_query(login: str, password: str, long_lived: bool = False) -> dict:
    """Проверка логина/пароля. Возвращает access + refresh токены."""
    async with session_create() as session:
        user = (
            await session.scalars(select(Users).where(Users.login == login))
        ).one_or_none()

        if user is None or user.disabled:
            logger.warning(f"Вход отклонён: {login} отсутствует/заблокирован.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.check_password(password=password):
            logger.warning(f"Вход отклонён: неверный пароль для {login}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_token({"sub": user.login}, token_type="access")
        refresh_token = create_token({"sub": user.login}, token_type="refresh")
        logger.info(f"Пользователь {user.login} авторизован.")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "login": user.login,
                "user_name": user.user_name,
                "is_admin": user.is_admin,
            },
        }


async def refresh_access_token(refresh_token: str) -> dict:
    """Обмен refresh-токена на новый access-токен."""
    login = decode_token(refresh_token, expected_type="refresh")
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh-токен невалиден или истёк.",
        )

    async with session_create() as session:
        user = (
            await session.scalars(select(Users).where(Users.login == login))
        ).one_or_none()
        if user is None or user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь заблокирован или не существует.",
            )

    new_access = create_token({"sub": login}, token_type="access")
    logger.info(f"Обновлён access-токен для {login}.")
    return {"access_token": new_access, "token_type": "bearer"}
