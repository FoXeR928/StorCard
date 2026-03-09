from fastapi import APIRouter, Response, Depends, HTTPException, Form
from loguru import logger
from src.database.repository.repo_auth import authenticate_user
from src.api.depends import get_current_user
from src.core.responses import api_response, error_500
from src.database.repository.repo_config import get_all_configs_dict

auth_api = APIRouter(prefix="/v1/auth", tags=["Авторизация"])


@auth_api.post("/login", summary="Вход в систему")
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
        conf = get_all_configs_dict()
        key = "long_token" if expires_use else "short_token"
        max_age = int(conf.get(key, 3600))
        response.set_cookie(
            key="token",
            value=result["access_token"],
            httponly=True,
            samesite="lax",
            max_age=max_age,
        )
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ошибка входа {username}: {e}")
        return error_500("Внутренняя ошибка сервера")


@auth_api.post("/logout", summary="Выход")
async def logout_api(response: Response, user=Depends(get_current_user)):
    response.delete_cookie(key="token")
    return api_response(True, "Пользователь деавторизирован", 200)


@auth_api.get("/me", summary="Профиль")
async def get_me(user=Depends(get_current_user)):
    return api_response(True, "Данные получены", 200, user=user)
