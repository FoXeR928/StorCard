from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel
from typing import Any
from loguru import logger

from api.api_auth import User, get_current_user
try:
    cards_app = APIRouter(prefix="/cards", tags=["Карты"])
    logger.debug("Инициализирован API карт")
except Exception as err:
    logger.error(f"Ошибка инициализации API: {err}")

@cards_app.get("/all/get", summary="Получение всех карт в базе")
async def get_cards_all_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    if current_user.is_admin == True:
        result = True
    else:
        result = {
            "result": False,
            "message": "Доступно только администратору",
            "category": "warning",
            "cod": 403,
        }
    response.status_code = result["cod"]
    del result["cod"]
    return result