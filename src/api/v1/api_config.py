from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from loguru import logger
from src.api.depends import get_current_user
from src.database.repository.repo_config import (
    get_configs_list_api,
    update_config_query,
)
from src.api.schemas.schemas_config import ConfigUpdate
import src.core.system as system

config_api = APIRouter(prefix="/configs", tags=["Конфиги"])


@config_api.get("/get", summary="Получение всех конфигов")
async def get_configs_app_api(user=Depends(get_current_user)):
    if not user.get("is_admin"):
        raise HTTPException(403, "Доступ только для администраторов")
    return get_configs_list_api()


@config_api.patch("/update", summary="Обновление конфига")
async def update_config_app_api(
    config_data: ConfigUpdate,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    if not user.get("is_admin"):
        raise HTTPException(403, "Доступ запрещен")
    result = update_config_query(name=config_data.name, value=config_data.value)
    if result.get("result"):
        logger.warning(
            f"Конфиг {config_data.name} изменен. Запланирована перезагрузка."
        )
        background_tasks.add_task(system.reboot_server, delay=2)

    return result
