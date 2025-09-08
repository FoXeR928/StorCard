from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from loguru import logger

templates = Jinja2Templates(directory="front/public/tempales/")

try:
    admin_pages_app=APIRouter(prefix="/admin", tags=["Администрирование веб-интерфейс"])
    logger.debug("Инициализирован веб-интерфейс администрирования")
except Exception as err:
    logger.error(f"Не удалось инициализировать веб-интерфейс администрирования: {err}")

@admin_pages_app.get("/", summary="Администрирование")
async def admin_page(request: Request):
    return templates.TemplateResponse(
        name="admin/admin.html", context={"request": request}
    )