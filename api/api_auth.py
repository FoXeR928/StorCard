from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy import select

from db.db_create import session_create, Users
from db.db_auth import auth_user_query, decode_token, refresh_access_token
from core.schemas import UserSchema

auth_app = APIRouter(prefix="/auth", tags=["Авторизация"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    login = decode_token(token=token, expected_type="access")
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with session_create() as session:
        user = (
            await session.scalars(select(Users).where(Users.login == login))
        ).one_or_none()

        if user is None or user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь заблокирован или не существует.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserSchema.model_validate(user)


@auth_app.post("/login", summary="Авторизация для получения токена (OAuth2)")
async def login_api(
    auth: OAuth2PasswordRequestForm = Depends(),
    remember_me: bool = False,
):
    return await auth_user_query(
        login=auth.username,
        password=auth.password,
        remember_me=remember_me,
    )


class RefreshSchema(BaseModel):
    refresh_token: str


@auth_app.post(
    "/refresh",
    summary="Обмен refresh-токена на новый access-токен",
)
async def refresh_api(data: RefreshSchema):
    """Клиент вызывает этот эндпоинт при получении 401."""
    return await refresh_access_token(refresh_token=data.refresh_token)


@auth_app.post("/logout", summary="Выход из учетной записи")
async def logout_api(current_user: UserSchema = Depends(get_current_user)):
    return {
        "result": True,
        "message": f"Пользователь {current_user.login} деавторизован. Удалите токены на клиенте.",
    }
