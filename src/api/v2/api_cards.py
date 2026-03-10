import uuid
from fastapi import APIRouter, Depends, Response
from src.api.depends import get_current_user
from src.api.schemas.schemas_cards import AddCard, CardBase, UpdateCard
from src.database.repository.repo_cards import (
    sync_cards_query
)

cards_api_v2 = APIRouter(prefix="/v2/cards", tags=["Карты"])


@cards_api.post("/sync", summary="Синхранизация карты")
def sync_cards(response:Response,current_user:Depends(get_current_user)):
    result=sync_cards_query()
    response.status_code=result.result.get("code", 200)
    return result