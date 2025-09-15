from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel
from typing import Any
from loguru import logger

from api.api_auth import User, get_current_user
from db_modules.db_query_config import (
    get_configs_query,
    update_config_query,
)

try:
    config_app = APIRouter(prefix="/configs", tags=["Конфиги"])
    logger.debug("Инициализирован API конфигов")
except Exception as err:
    logger.error(f"Ошибка инициализации API: {err}")


class ConfigUpdate(BaseModel):
    name: str
    value: Any


@config_app.get("/app/get", summary="Получение конфигов приложения")
async def get_configs_app_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    if current_user.is_admin == True:
        result = get_configs_query()
    else:
        result = {
            "result": False,
            "message": "Доступно только администратору",
            "category": "warning",
            "cod": 403,
        }
    response.status_code = result["cod"]
    del result["cod"]
    return result


@config_app.patch("/app/update", summary="Обновление конфига приложения")
async def update_config_app_api(
    config_data: ConfigUpdate,
    response: Response,
    current_user: User = Depends(get_current_user),
):
    if current_user.is_admin == True:
        result = update_config_query(name=config_data.name, value=config_data.value)
    else:
        result = {
            "result": False,
            "message": "Доступно только администратору",
            "category": "warning",
            "cod": 403,
        }
    response.status_code = result["cod"]
    del result["cod"]
    return result
