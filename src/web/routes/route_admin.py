from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from loguru import logger
from src.api.main_app import TEMPLATE_DIR

templates = Jinja2Templates(directory=TEMPLATE_DIR)

admin_route = APIRouter(prefix="", tags=["Администрирование веб-интерфейс"])

@admin_route.get("/admin", summary="Администрирование")
"""Отображает страницы администрирования приложения."""
async def admin_page(request: Request):
    return templates.TemplateResponse(
        name="screens/adminScreen.html", context={"request": request}
    )

logger.debug("Веб-интерфейс администратор инициализирован")