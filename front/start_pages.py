from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from loguru import logger

templates = Jinja2Templates(directory="front/public/tempales/")

try:
    start_pages_app=APIRouter(prefix="", tags=["Стартовая страница веб-интерфейс"])
    logger.debug("Инициализирован веб-интерфейс")
except Exception as err:
    logger.error(f"Ошибка инициализации веб-интерфейс: {err}")


@start_pages_app.get("/", summary="Создание установочных конфигов приложения")
async def start_configs_app_page(request: Request):
    return templates.TemplateResponse(name="config_start/start.html",context={'request': request})
