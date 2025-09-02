from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates
from loguru import logger

templates = Jinja2Templates(directory="front/public/templates/")

try:
    start_pages_app=APIRouter(prefix="", tags=["\u0421\u0442\u0430\u0440\u0442\u043e\u0432\u0430\u044f \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u0432\u0435\u0431-\u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441"])
    logger.debug("\u0418\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d API \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u044b\u0439")
except Exception as err:
    logger.error(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438 API: {err}")


@start_pages_app.get("/", summary="\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043e\u0447\u043d\u044b\u0445 \u043a\u043e\u043d\u0444\u0438\u0433\u043e\u0432 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u044f")
async def start_configs_ai_api(request: Request):
    return templates.TemplateResponse(name="config_start/start.html",context={'request': request})