from fastapi import APIRouter, Response, Depends, UploadFile
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger

from api.api_auth import User, get_current_user
from db_modules.db_query_cards import (
    all_cards_query,
    user_cards_query,
    get_card_query,
    add_card_query,
    update_card_name_query,
    update_card_about_query,
    update_card_code_query,
    update_card_image_query,
    delete_card_query,
    update_card_own_query,
    add_card_access_query,
)
from api.api_answer import error_access,error_auth

try:
    cards_app = APIRouter(prefix="/cards", tags=["Карты"])
    logger.debug("Инициализирован API карт")
except Exception as err:
    logger.error(f"Ошибка инициализации API: {err}")


class AddCard(BaseModel):
    name: str
    about: Optional[str] = None
    code: str
    code_type: str


class Card(BaseModel):
    id: int


class UpdateCardName(Card):
    name: str


class UpdateCardAbout(Card):
    about: str


class UpdateCardCode(Card):
    code: str
    code_type: str


class UpdateCardOwn(Card):
    own: str


class AddCardAccess(Card):
    login: str


@cards_app.get("/get", summary="Получение всех карт в базе")
async def get_cards_all_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    if current_user==None:
        result=error_auth
    else:
        if current_user.is_admin == True:
            result = all_cards_query()
        else:
            result = error_access
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.get("/user/get", summary="Получение всех карт в базе")
async def get_cards_user_api(
    response: Response, current_user: User = Depends(get_current_user)
):
    result = user_cards_query(user=current_user)
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.get("/card/get", summary="Получение карты из базе")
async def get_card_api(
    response: Response, card_id: int, current_user: User = Depends(get_current_user)
):
    result = get_card_query(card_id=card_id, user=current_user)
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.post("/add", summary="Добавление карты в базу")
async def add_card_api(
    response: Response, add: AddCard, current_user: User = Depends(get_current_user)
):
    result = add_card_query(
        name=add.name,
        about=add.about,
        user=current_user,
        code=add.code,
        code_type=add.code_type,
    )
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.post("/add/access", summary="Добавление доступа к карте")
async def add_card_access_api(
    response: Response,
    access: AddCardAccess,
    current_user: User = Depends(get_current_user),
):
    result = add_card_access_query(
        card_id=access.id, login=access.login, user=current_user
    )
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.patch("/update/name", summary="Обновление имени карты")
async def update_card_name_api(
    response: Response,
    name: UpdateCardName,
    current_user: User = Depends(get_current_user),
):
    result = update_card_name_query(card_id=name.id, user=current_user, name=name.name)
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.patch("/update/about", summary="Обновление описания карты")
async def update_card_about_api(
    response: Response,
    about: UpdateCardAbout,
    current_user: User = Depends(get_current_user),
):
    result = update_card_about_query(
        card_id=about.id, user=current_user, about=about.about
    )
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.patch("/update/code", summary="Обновление кода карты")
async def update_card_code_api(
    response: Response,
    code: UpdateCardCode,
    current_user: User = Depends(get_current_user),
):
    result = update_card_code_query(
        card_id=code.id, user=current_user, code=code.code, code_type=code.code_type
    )
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.patch("/update/own", summary="Обновление владельца карты")
async def update_card_code_api(
    response: Response,
    own: UpdateCardOwn,
    current_user: User = Depends(get_current_user),
):
    result = update_card_own_query(card_id=own.id, user=current_user, own=own.own)
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.patch("/update/image", summary="Обновление кода карты")
async def update_card_image_api(
    response: Response,
    id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
):
    result = update_card_image_query(
        card_id=id, user=current_user, image=file.file.read()
    )
    response.status_code = result["cod"]
    del result["cod"]
    return result


@cards_app.delete("/delete", summary="Удаление карты")
async def delete_card_api(
    response: Response, card: Card, current_user: User = Depends(get_current_user)
):
    result = delete_card_query(card_id=card.id, user=current_user)
    response.status_code = result["cod"]
    del result["cod"]
    return result
