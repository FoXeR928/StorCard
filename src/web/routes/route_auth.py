from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from loguru import logger
from src.api.main_app import TEMPLATE_DIR

templates = Jinja2Templates(directory=TEMPLATE_DIR)

auth_route = APIRouter(prefix="", tags=["Авторизация веб-интерфейс"])
    
@auth_route.get("/", summary="Авторизация")
"""Отображает стартовый экран установки приложения."""
async def auth_page(request: Request):
    return templates.TemplateResponse(
        name="screens/authScreen.html", context={"request": request}
    )

logger.debug("Веб-интерфейс авторизации инициализирован")