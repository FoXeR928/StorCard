from fastapi import APIRouter, Response, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from data.config_modules.os_module import reboot_server
from data.db_modules.db_query_config_start import create_config_app_start_query

config_start_app = APIRouter(prefix="/config/app/start", tags=["Стартовая страница"])


class ConfigStartApp(BaseModel):
    app_port: int = 7000
    sql_driver: str = "sqlite"
    sql_host: Optional[str] = None
    sql_port: Optional[int] = None
    sql_db: Optional[str] = "storcard_db"
    sql_user: Optional[str] = None
    sql_password: Optional[str] = None
    db_path: Optional[str] = "./instance"
    front: Optional[bool] = True


@config_start_app.post("/create", summary="Создание установочных конфигов приложения")
async def start_configs_app_api(
    configs: ConfigStartApp,
    response: Response,
    background_task: BackgroundTasks,
):
    result = create_config_app_start_query(**configs.model_dump())
    response.status_code = result["cod"]
    if result["result"] == True:
        background_task.add_task(reboot_server, deplay=2)
        logger.info("Задача перезагрузки сервера добавлена в очередь")
    return result
