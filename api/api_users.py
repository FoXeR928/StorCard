from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

# Импортируем нашу зависимость авторизации, схему юзера и репозиторий управления пользователями
from api.api_auth import get_current_user, UserSchema
from db.db_users import UserRepository

users_app = APIRouter(prefix="/users", tags=["Пользователи"])


class RegistrationUserSchema(BaseModel):
    login: str
    user_name: str
    password: str


class UpdatePasswordSchema(BaseModel):
    login: str
    password: str


class UpdateRoleSchema(BaseModel):
    login: str
    is_admin: bool = False



@users_app.get("/", summary="Получение списка всех пользователей (Только для Администратора)")
async def get_users_api(current_user: UserSchema = Depends(get_current_user)):
    """Возвращает массив всех учетных записей. Доступно только администраторам системы."""
    return UserRepository.get_all_users(current_user=current_user)


@users_app.post("/registration", status_code=status.HTTP_201_CREATED, summary="Создание/Регистрация нового пользователя")
async def registration_user_api(
    registration_data: RegistrationUserSchema,
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Создает новую учетную запись в базе данных. 
    Доступно только администраторам системы.
    """
    return UserRepository.register_user(
        login=registration_data.login,
        user_name=registration_data.user_name,
        password=registration_data.password,
        current_user=current_user
    )


@users_app.patch("/password", summary="Смена пароля пользователя")
async def update_password_user_api(
    password_data: UpdatePasswordSchema,
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Позволяет сменить пароль. 
    Пользователь может менять свой пароль, администратор — любой аккаунт.
    """
    return UserRepository.update_password(
        target_login=password_data.login,
        password=password_data.password,
        current_user=current_user
    )


@users_app.patch("/role", summary="Смена администраторской роли пользователя")
async def update_role_user_api(
    role_data: UpdateRoleSchema,
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Повышает или понижает уровень прав пользователя. 
    Доступно только администраторам системы с защитой от удаления последнего админа.
    """
    return UserRepository.update_role(
        target_login=role_data.login,
        is_admin=role_data.is_admin,
        current_user=current_user
    )


@users_app.delete("/{login}", summary="Полное удаление пользователя из системы")
async def delete_user_api(
    login: str,
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Каскадно удаляет пользователя и все связанные с ним доступы к картам.
    Доступно только администраторам системы с защитой от удаления последнего админа.
    """
    return UserRepository.delete_user(
        target_login=login,
        current_user=current_user
    )
