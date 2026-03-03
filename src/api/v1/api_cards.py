import uuid
from fastapi import APIRouter, Depends, UploadFile, Response
from src.api.depends import get_current_user
from src.core.responses import error_403
from src.api.schemas.schemas_cards import (
    AddCard,
    AddCardAccess,
    UpdateCardAbout,
    UpdateCardName,
    UpdateCardCode,
    UpdateCardOwn,
    CardBase,
)
from src.database.repository.repo_cards import (
    all_cards_query,
    add_card_query,
    get_card_query,
    user_cards_query,
    add_card_access_query,
    update_card_field,
    delete_card_query,
)

cards_api = APIRouter(prefix="/cards", tags=["Карты"])


def send_res(response: Response, result: dict):
    response.status_code = result.get("code", result.get("cod", 200))
    return result


@cards_api.get("/get", summary="Все карты (только Admin)")
async def get_all(res: Response, user=Depends(get_current_user)):
    if not user.is_admin:
        return send_res(res, error_403)
    return send_res(res, all_cards_query())


@cards_api.get("/user/get", summary="Карты текущего пользователя")
async def get_user_cards(res: Response, user=Depends(get_current_user)):
    return send_res(res, user_cards_query(user=user))


@cards_api.get("/card/get", summary="Получение одной карты")
async def get_card(res: Response, card_id: uuid.UUID, user=Depends(get_current_user)):
    return send_res(res, get_card_query(card_id=card_id, user=user))


@cards_api.post("/add", summary="Добавление карты")
async def add_card(res: Response, data: AddCard, user=Depends(get_current_user)):
    return send_res(res, add_card_query(**data.dict(), user=user))


@cards_api.post("/add/access", summary="Выдача доступа к карте")
async def add_access(
    res: Response, data: AddCardAccess, user=Depends(get_current_user)
):
    return send_res(
        res, add_card_access_query(card_id=data.id, login=data.login, user=user)
    )


@cards_api.patch("/update/name")
async def update_name(
    res: Response, data: UpdateCardName, user=Depends(get_current_user)
):
    return send_res(res, update_card_field(card_id=data.id, name=data.name, user=user))


@cards_api.patch("/update/about")
async def update_about(
    res: Response, data: UpdateCardAbout, user=Depends(get_current_user)
):
    return send_res(
        res, update_card_field(card_id=data.id, about=data.about, user=user)
    )


@cards_api.patch("/update/code")
async def update_code(
    res: Response, data: UpdateCardCode, user=Depends(get_current_user)
):
    return send_res(res, update_card_field(**data.model_dump(), user=user))


@cards_api.patch("/update/image")
async def update_image(
    res: Response, id: uuid.UUID, file: UploadFile, user=Depends(get_current_user)
):
    image_data = await file.read()
    return send_res(res, update_card_field(card_id=id, user=user, image=image_data))


@cards_api.delete("/delete")
async def delete_card(res: Response, data: CardBase, user=Depends(get_current_user)):
    return send_res(res, delete_card_query(card_id=data.id, user=user))
