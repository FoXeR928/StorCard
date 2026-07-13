from fastapi import APIRouter, Depends, Response
from src.database.repository.repo_auth import get_current_user
from src.web.resources.schemas.schemas_users import (
    RegistrationUser,
    UpdateUser,
)
from src.database.repository.repo_users import (
    get_users_query,
    registration_user_query,
    update_user_query,
    delete_user_query,
)

api_users_v1 = APIRouter(prefix="/v1/users", tags=["Пользователи"])


@api_users_v1.get("/get", summary="Получение списка пользователей")
async def get_users_api(response: Response, current_user=Depends(get_current_user)):
    return get_users_query(current_user)


@api_users_v1.post(
    "/registration",
    summary="Создание пользователя",
)
async def registration_user_api(
    response: Response, data: RegistrationUser, current_user=Depends(get_current_user)
):
    return registration_user_query(current_user, **data.model_dump())


@api_users_v1.patch("/change/", summary="Смена роли пользователя")
async def update_role_user_api(
    response: Response, data: UpdateUser, current_user=Depends(get_current_user)
):
    return update_user_query(
        requester=current_user, **data.model_dump(exclude_unset=True)
    )


@api_users_v1.delete("/delet", summary="Удаление пользователя")
async def delet_user_api(
    response: Response, login: str, current_user=Depends(get_current_user)
):
    return delete_user_query(requester=current_user, login=login)
