from sqlalchemy import select
from loguru import logger
import src.core.security as security
from src.database.models.model_users import Users
import src.database.engine as engine
from src.core.responses import api_response, error_401, error_500


def get_user_by_login(login: str):
    with engine.SessionLocal() as session:
        return session.execute(
            select(Users.login, Users.user_name, Users.is_admin).where(
                Users.login == login
            )
        ).one_or_none()


def authenticate_user(login: str, password: str, long_session: bool):
    try:
        with engine.SessionLocal() as session:
            user = session.scalars(
                select(Users).where(Users.login == login)
            ).one_or_none()
            if not user or not user.check_password(password):
                error_401()
            token = security.create_access_token(
                login=user.login, expires_use=long_session
            )
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
