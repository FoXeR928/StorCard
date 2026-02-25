from fastapi import APIRouter, Response, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Any
from loguru import logger

from data.config_modules.os_module import reboot_server
from network.api.api_auth import User, get_current_user
from data.db_modules.db_query_config import (
    get_configs_query,
    update_config_query,
)
from network.api.api_answer import error_access

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
    if current_user != None and current_user.is_admin == True:
        result = get_configs_query()
    else:
        result = error_access
    response.status_code = result["cod"]
    return result


@config_app.patch("/app/update", summary="Обновление конфига приложения")
async def update_config_app_api(
    config_data: ConfigUpdate,
    response: Response,
    current_user: User = Depends(get_current_user),
    background_task:BackgroundTasks
):
    if current_user.is_admin == True:
        result = update_config_query(name=config_data.name, value=config_data.value)
    else:
        result = error_access
    response.status_code = result["cod"]
    if result["result"]==True:
        background_task(reboot_server)
    return result
