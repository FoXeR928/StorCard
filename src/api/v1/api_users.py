from fastapi import APIRouter, Depends, HTTPException, status
from src.api.depends import get_current_user
from src.api.schemas.schemas_users import RegistrationUser, UpdatePassword, UpdateRole
from src.database.repository.repo_users import (
    get_users_query,
    registration_user_query,
    update_password_user_query,
    update_role_user_query,
    delete_user_query,
)

users_api = APIRouter(prefix="/users", tags=["Пользователи"])


@users_api.get("/get", summary="Получение списка пользователей")
async def get_users_api(_=Depends(admin_required)):
    return get_users_query()


@users_api.post(
    "/registration",
    summary="Создание пользователя",
    status_code=status.HTTP_201_CREATED,
)
async def registration_user_api(requester: current_user, data: RegistrationUser):
    return registration_user_query(**data.model_dump())


@users_api.patch("/change/password", summary="Смена пароля пользователя")
async def update_password_user_api(
    data: UpdatePassword, current_user=Depends(get_current_user)
):
    return update_password_user_query(requester=current_user, **data.model_dump())


@users_api.patch("/change/", summary="Смена роли пользователя")
async def update_role_user_api(data: UpdateRole, current_user=Depends(admin_required)):
    return update_role_user_query(
        requester=current_user, **data.model_dump(exclude_unset=True)
    )


@users_api.patch("/change/role", summary="Смена роли пользователя")
async def update_role_user_api(data: UpdateRole, current_user=Depends(admin_required)):
    return update_role_user_query(requester=current_user, **data.model_dump())


@users_api.delete("/delet", summary="Удаление пользователя")
async def delet_user_api(login: str, current_user=Depends(admin_required)):
    return delete_user_query(requester=current_user, login=login)
