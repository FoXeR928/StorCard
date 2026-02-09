from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional

from db_modules.db_query_auth import (
    auth_query,
    logout_query,
    decode_token,
    get_current_user_query,
)

auth_app = APIRouter(
    prefix="/auth",
    tags=["Авторизация"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class User(BaseModel):
    login: str
    name: Optional[str] = None
    is_admin: bool


class Auth(User):
    password: str
    disabled: bool = False


async def get_current_user(token: str = Depends(oauth2_scheme)):
    login = decode_token(token=token)
    if login == None:
        user=(None,None,None)
    else:
        user = get_current_user_query(login=login)
        return User(login=user[0], name=user[1], is_admin=bool(int(user[2])))


@auth_app.post(
    "/login",
    summary="\u0410\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f \u0434\u043b\u044f \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u0438\u044f \u0442\u043e\u043a\u0435\u043d\u0430",
)
async def login_api(response: Response, auth: OAuth2PasswordRequestForm = Depends()):
    result = auth_query(login=auth.username, password=auth.password)
    response.status_code = result["cod"]
    del result["cod"]
    return result


@auth_app.post(
    "/logout",
    summary="\u0412\u044b\u0445\u043e\u0434 \u0438\u0437 \u0443\u0447\u0435\u0442\u043d\u043e\u0439 \u0437\u0430\u043f\u0438\u0441\u0438",
)
async def logout_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    result = logout_query(login=current_user.login)
    response.status_code = result["cod"]
    del result["cod"]
    return result
