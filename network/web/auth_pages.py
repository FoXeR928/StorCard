from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from loguru import logger

templates = Jinja2Templates(directory="network/public/tempales")

try:
    auth_pages_app = APIRouter(prefix="", tags=["Авторизация веб-интерфейс"])
    logger.debug("Auth web interfase initialized")
except Exception as err:
    logger.error(f"Не удалось инициализировать веб-интерфейс авторизации: {err}")


@admin_pages_app.get("/", summary="Авторизация")
async def auth_page(request: Request):
    return templates.TemplateResponse(
        name="screens/authScreen.html", context={"request": request}
    )