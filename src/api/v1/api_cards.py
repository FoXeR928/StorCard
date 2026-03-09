import uuid
from fastapi import APIRouter, Depends, Response
from src.api.depends import get_current_user
from src.api.schemas.schemas_cards import AddCard, CardBase, UpdateCard
from src.database.repository.repo_cards import (
    add_card_query,
    cards_query,
    update_card_query,
    delete_card_query,
)

cards_api = APIRouter(prefix="/v1/cards", tags=["Карты"])


@cards_api.get("/get", summary="Получение карт")
async def get_cards(response: Response, current_user=Depends(get_current_user)):
    result = cards_query(current_user)
    response.status_code = result.get("code", 200)
    return result


@cards_api.post("/add", summary="Добавление карты")
async def add_card(response: Response, data: AddCard, user=Depends(get_current_user)):
    result = add_card_query(**data.model_dump(exclude_unset=True), user=user)
    response.status_code = result.get("code", 200)
    return result


@cards_api.patch("/update/")
async def update_name(
    response: Response, data: UpdateCard, user=Depends(get_current_user)
):
    result = update_card_query(**data.model_dump(exclude_unset=True), user=user)
    response.status_code = result.get("code", 200)
    return result


@cards_api.delete("/delete")
async def delete_card(
    response: Response, data: CardBase, user=Depends(get_current_user)
):
    result = delete_card_query(card_id=data.id, user=user)
    response.status_code = result.get("code", 200)
    return result
