from loguru import logger
from fastapi import HTTPException, status
from sqlalchemy import select, update, delete, func

from db.db_create import session_create, Users
from api.api_auth import UserSchema


class UserRepository:
    """
    Объединенный и оптимизированный репозиторий для управления пользователями системы StorCard.
    """

    @staticmethod
    def _verify_admin_protection(session, target_login: str, current_user_login: str):
        """
        Внутренний хелпер для проверки 'защиты от дурака'.
        Гарантирует, что единственный администратор в системе не сможет удалить себя 
        или лишить себя администраторских прав.
        """
        target_user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
        
        if target_user and target_user.is_admin:
            admins_count = session.scalar(select(func.count(Users.login)).where(Users.is_admin == True))
            
            if admins_count <= 1 and target_login == current_user_login:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Действие заблокировано: в системе должен оставаться как минимум один администратор."
                )

    @classmethod
    def get_all_users(cls, current_user: UserSchema) -> list:
        """Возвращает список всех пользователей системы. Доступно только администраторам."""
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа.")
            
        with session_create() as session:
            users_get = session.execute(
                select(
                    Users.id, Users.login, Users.user_name, 
                    Users.is_admin, Users.disabled, 
                    Users.date_create, Users.date_update
                )
            ).all()
            logger.debug(f"Администратор {current_user.login} успешно запросил список пользователей.")
            return [dict(row._mapping) for row in users_get]

    @classmethod
    def register_user(cls, login: str, user_name: str, password: str, current_user:UserSchema) -> dict:
        """Регистрация нового аккаунта в системе."""
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа.")

        with session_create() as session:
            existing_user = session.scalars(select(Users).where(Users.login == login)).one_or_none()
            if existing_user:
                logger.info(f"Отказ в регистрации: логин '{login}' уже занят.")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким логином уже зарегистрирован."
                )

            try:
                new_user = Users(login=login, user_name=user_name, is_admin=False)
                new_user.set_password(password)
                
                session.add(new_user)
                session.commit()
                
                logger.success(f"Создан новый пользователь: {login}")
                return {"result": True, "message": "Пользователь успешно зарегистрирован."}
            except Exception as err:
                logger.error(f"Не удалось зарегистрировать пользователя {login}. Ошибка: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера.")

    @classmethod
    def update_password(cls, target_login: str, password: str, current_user: UserSchema) -> dict:
        """Обновление пароля. Пользователь может менять свой пароль, администратор — любой."""
        if current_user.login != target_login and not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет прав для изменения пароля этого пользователя.")

        with session_create() as session:
            user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

            try:
                user.set_password(password)
                session.commit()
                logger.success(f"Пароль пользователя {target_login} изменен пользователем {current_user.login}")
                return {"result": True, "message": "Пароль успешно изменен."}
            except Exception as err:
                logger.error(f"Ошибка изменения пароля {target_login}: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера.")

    @classmethod
    def update_role(cls, target_login: str, is_admin: bool, current_user: UserSchema) -> dict:
        """Изменение администраторских прав пользователя. Доступно только администраторам."""
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа.")

        with session_create() as session:
            user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

            if not is_admin:
                cls._verify_admin_protection(session, target_login, current_user.login)

            try:
                user.is_admin = is_admin
                session.commit()
                logger.success(f"Роль пользователя {target_login} изменена на is_admin={is_admin} администратором {current_user.login}")
                return {"result": True, "message": "Роль пользователя успешно изменена."}
            except Exception as err:
                logger.error(f"Ошибка обновления роли {target_login}: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера.")

    @classmethod
    def delete_user(cls, target_login: str, current_user: UserSchema) -> dict:
        """Полное удаление пользователя из системы. Доступно только администраторам."""
        if not current_user.is_admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа.")

        with session_create() as session:
            user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

            cls._verify_admin_protection(session, target_login, current_user.login)

            try:
                session.execute(delete(Users).where(Users.login == target_login))
                session.commit()
                logger.success(f"Пользователь {target_login} успешно удален администратором {current_user.login}")
                return {"result": True, "message": "Пользователь успешно удален из системы."}
            except Exception as err:
                logger.error(f"Не удалось удалить пользователя {target_login}. Ошибка: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера.")
