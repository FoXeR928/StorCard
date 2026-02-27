from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from loguru import logger
from src.api.main_app import TEMPLATE_DIR

templates = Jinja2Templates(directory=TEMPLATE_DIR)

install_route = APIRouter(prefix="", tags=["Установочная страница веб-интерфейс"])

@install_route.get("/", summary="Установка приложения")
"""Отображает страницы авторизации."""
async def install_page(request: Request):
    return templates.TemplateResponse(
        name="screens/startScreen.html", context={"request": request}
    )

logger.debug("Веб-интерфейс установки инициализирован")