from sqlalchemy import select, update, delete, func
from loguru import logger
from typing import Any
from src.core.responses import api_response, error_404, error_500, error_403
from src.database.models.model_users import Users
import src.database.engine as engine


def get_users_query(requester):
    if not requester.is_admin:
        return error_403()
    try:
        with engine.SessionLocal() as session:
            users = (
                session.execute(
                    select(
                        Users.login,
                        Users.user_name,
                        Users.is_admin,
                        Users.disabled,
                        Users.date_create,
                        Users.date_update,
                    )
                )
                .mappings()
                .all()
            )
        logger.debug("Список пользователей успешно получен")
        return api_response(True, "Пользователи получены", users)
    except Exception as err:
        logger.error(f"Ошибка получения пользователей: {err}")
        return error_500()


def registration_user_query(
    requester,
    login: str,
    user_name: str,
    password: str,
):
    if not requester.is_admin:
        return error_403()
    with engine.SessionLocal() as session:
        try:
            exists = session.scalar(select(Users).where(Users.login == login))
            if exists:
                return api_response(
                    False, "Пользователь уже существует", 409, "warning"
                )
            new_user = Users(login=login, user_name=user_name)
            new_user.set_password(password)
            session.add(new_user)
            session.commit()
            logger.success(f"Пользователь {login} создан")
            return api_response(True, "Пользователь создан", 201)
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка регистрации: {err}")
            return error_500()


def update_user_query(requester: Any, login: str, **values):
    if not (requester.is_admin or requester.login == login):
        return error_403("Нет прав на изменение")
    if not values:
        return api_response(True, "Нет данных для обновления", 200)
    with engine.SessionLocal() as session:
        try:
            user = session.scalar(select(Users).where(Users.login == login))
            if not user:
                return error_404("Пользователь не найден")
            if "password" in values:
                user.set_password(values.pop("password"))
            for key, value in values.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            return api_response(True, "Информация изменена", 201)
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка изменения: {err}")
            return error_500()


def delete_user_query(requester: Any, login: str):
    if not requester.is_admin:
        return error_403("Нет права на удаление")
    with engine.SessionLocal() as session:
        try:
            result = session.execute(delete(Users).where(Users.login == login))
            if result.rowcount == 0:
                return error_404("Пользователь не найден")
            session.commit()
            logger.success(f"Пользователь {login} удален")
            return api_response(True, "Пользователь удален", 201)
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка удаления: {err}")
            return error_500()


"""Проверено"""
