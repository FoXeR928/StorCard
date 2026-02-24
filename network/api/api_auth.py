from fastapi import APIRouter, Response, Depends, HTTPException, Request, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

from data.db_modules.db_query_auth import (
    auth_query,
    decode_token,
    get_current_user_query,
)
from data.db_modules.db_query_config import get_config

auth_app = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        if authorization:
            return await super().__call__(request)
        token = request.cookies.get("token")
        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return token


class CustomOAuth2Form(OAuth2PasswordRequestForm):
    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        expires_use: bool = Form(False),
        scope: str = Form(""),
        client_id: Optional[str] = Form(None),
        client_secret: Optional[str] = Form(None),
    ):
        super().__init__(
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.expires_use = expires_use


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="auth/login")


class User(BaseModel):
    login: str
    name: Optional[str] = None
    is_admin: bool


class Auth(User):
    password: str
    disabled: bool = False


async def get_current_user(token: str = Depends(oauth2_scheme)):
    login = decode_token(token=token)
    if login is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_current_user_query(login=login)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(login=user[0], name=user[1], is_admin=bool(int(user[2])))


@auth_app.post(
    "/login",
    summary="Login API",
)
async def login_api(response: Response, auth: CustomOAuth2Form = Depends()):
    result = auth_query(
        login=auth.username, password=auth.password, tokenTime=auth.expires_use
    )
    if result["cod"] not in [200, 201]:
        raise HTTPException(status_code=result["cod"], detail=result["message"])
    token = result["access_token"]
    max_age = (
        int(get_config("long_token"))
        if auth.expires_use
        else int(get_config("short_token"))
    )
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,
        path="/",
        samesite="lax",
        max_age=max_age,
    )
    response.status_code = result["cod"]
    return result


@auth_app.post(
    "/logout",
    summary="Logout API",
)
async def logout_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    response.delete_cookie(key="token", path="/", httponly=True, samesite="lax")
    result = {
        "result": True,
        "message": "Пользователь деавторизирован",
        "category": "success",
        "cod": 201,
    }
    response.status_code = result["cod"]
    return result
