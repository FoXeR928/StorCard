import uuid
from fastapi import APIRouter, Depends, UploadFile, Response
from src.api.depends import get_current_user
from src.core.responses import error_403
from src.api.schemas.schemas_cards import AddCard, AddCardAccess, CardBase, UpdateCard
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


@cards_api.get("/get", summary="Все карты (только Admin)")
async def get_all(res: Response, user=Depends(get_current_user)):
    if not user.is_admin:
        return error_403
    return all_cards_query()


@cards_api.get("/user/get", summary="Карты текущего пользователя")
async def get_user_cards(res: Response, user=Depends(get_current_user)):
    return user_cards_query(user=user)


@cards_api.get("/card/get", summary="Получение одной карты")
async def get_card(res: Response, card_id: uuid.UUID, user=Depends(get_current_user)):
    return get_card_query(card_id=card_id, user=user)


@cards_api.post("/add", summary="Добавление карты")
async def add_card(res: Response, data: AddCard, user=Depends(get_current_user)):
    return add_card_query(**data.model_dump(exclude_unset=True), user=user)


@cards_api.post("/add/access", summary="Выдача доступа к карте")
async def add_access(
    res: Response, data: AddCardAccess, user=Depends(get_current_user)
):
    return add_card_access_query(card_id=data.id, login=data.login, user=user)


@cards_api.patch("/update/")
async def update_name(res: Response, data: UpdateCard, user=Depends(get_current_user)):
    return update_card_field(card_id=data.id, name=data.name, user=user)


@cards_api.delete("/delete")
async def delete_card(res: Response, data: CardBase, user=Depends(get_current_user)):
    return delete_card_query(card_id=data.id, user=user)
