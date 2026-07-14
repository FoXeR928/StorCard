from fastapi import APIRouter, Depends, Response
from web.resources.schemas.schemas_cards_sync import SyncShem
from web.api.api_auth import get_current_user
from database.repository.repo_cards import sync_cards_query

api_cards = APIRouter(prefix="/cards", tags=["Карты"])


@api_cards.post("/sync", summary="Синхранизация карты")
async def sync_cards(
    sync_cards: SyncShem, response: Response, current_user=Depends(get_current_user)
):
    result = sync_cards_query(requester=current_user, data=sync_cards)
    response.status_code = result.result.get("code", 200)
    return result
