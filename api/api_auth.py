from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select

from db.db_create import session_create, Users
from db.db_auth import auth_user_query, decode_token

auth_app = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserSchema(BaseModel):
    id: str
    login: str
    user_name: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserSchema:
    """
    Проверяет JWT токен, извлекает пользователя и возвращает схему данных.
    Если токен невалидный или пользователь заблокирован — генерирует 401 ошибку.
    """
    login = decode_token(token=token)
    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен доступа.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    with session_create() as session:
        user = session.scalars(select(Users).where(Users.login == login)).one_or_none()
        
        if user is None or user.disabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь заблокирован или не существует.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return UserSchema.from_orm(user)
    

@auth_app.post(
    "/login",
    summary="Авторизация для получения токена (OAuth2)",
)
async def login_api(auth: OAuth2PasswordRequestForm = Depends()):
    """
    Принимает username и password через стандартную форму.
    Возвращает access_token формата Bearer.
    """
    return auth_user_query(login=auth.username, password=auth.password)


@auth_app.post(
    "/logout",
    summary="Выход из учетной записи",
)
async def logout_api(current_user: UserSchema = Depends(get_current_user)):
    """
    Для Stateless JWT серверу не нужно чистить базу данных.
    Эндпоинт сообщает клиенту, что сессия завершена, и тот должен стереть токен у себя.
    """
    return {
        "result": True,
        "message": f"Пользователь {current_user.login} успешно деавторизован на сервере. Удалите токен на клиенте."
    }
