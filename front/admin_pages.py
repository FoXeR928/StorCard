from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from loguru import logger

templates = Jinja2Templates(directory="front/public/tempales/")

try:
    admin_pages_app=APIRouter(prefix="", tags=["Администрирование веб-интерфейс"])
    logger.debug("Инициализирован веб-интерфейс администрирования")
except Exception as err:
    logger.error(f"Не удалось инициализировать веб-интерфейс администрирования: {err}")

@admin_pages_app.get("/", summary="Авторизация")
async def auth_page(request: Request):
    return templates.TemplateResponse(
        name="admin/auth.html", context={"request": request}
    )

@admin_pages_app.get("/admin", summary="Администрирование")
async def admin_page(request: Request):
    return templates.TemplateResponse(
        name="admin/admin.html", context={"request": request}
    )