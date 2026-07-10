from fastapi import APIRouter, Response, BackgroundTasks
from loguru import logger
import core.core_system as core_system
import src.database.repository.repo_install as repo_install
from src.web.resources.schemas.schemas_install import InstallSchemas

install_api = APIRouter(prefix="/v1", tags=["Установка API"])


@install_api.post("/install", summary="Первичная настройка приложения")
async def install(
    configs: InstallSchemas,
    response: Response,
    background_task: BackgroundTasks,
):
    result = repo_install.install_db(**configs.model_dump())
    response.status_code = result.get("code", 201)
    if result.get("result"):
        background_task.add_task(core_system.reboot_server, delay=2)
        logger.info("Задача перезагрузки сервера добавлена в очередь")
    return result
