import jwt
from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from loguru import logger
from database.repository.repo_auth import authenticate_user, get_user_by_login
from web.resources.responses import api_response, error_500
from core.core_config import ACCESS_TOKEN, REFRESH_TOKEN

api_auth = APIRouter(prefix="/auth", tags=["Авторизация"])


class OAuth2CookieStack(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        header_auth = request.headers.get("Authorization")
        if header_auth:
            return await super().__call__(request)
        return request.cookies.get("token")


oauth2_scheme = OAuth2CookieStack(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(401, "Not authenticated")

    try:
        skey = get_config_val("skey")
        payload = jwt.decode(token, skey, algorithms=["HS256"], leeway=10)
        login = payload.get("sub")
    except Exception as err:
        logger.error(f"Непредвиденная ошибка декодирования: {err}")
        raise HTTPException(401, "Token invalid or expired")
    user = get_user_by_login(login)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@api_auth.post("/login", summary="Вход в систему")
async def login_api(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    expires_use: bool = Form(False),
):
    try:
        result = authenticate_user(username, password, expires_use)
        if not result["result"]:
            raise HTTPException(status_code=result["code"], detail=result["message"])
        if expires_use:
            max_age = REFRESH_TOKEN
        else:
            max_age = ACCESS_TOKEN
        response.set_cookie(
            key="token",
            value=result["access_token"],
            httponly=True,
            samesite="lax",
            max_age=max_age,
        )
        return result
    except HTTPException as error:
        raise error
    except Exception as error:
        logger.error(f"Ошибка входа {username}: {error}")
        return error_500("Внутренняя ошибка сервера")


@api_auth.post("/logout", summary="Выход")
async def logout_api(response: Response, user=Depends(get_current_user)):
    response.delete_cookie(key="token")
    return api_response(True, "Пользователь деавторизирован", 200)


@api_auth.get("/me", summary="Профиль")
async def get_me(user=Depends(get_current_user)):
    return api_response(True, "Данные получены", 200, user=user)
