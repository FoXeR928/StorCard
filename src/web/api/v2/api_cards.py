import uuid
from fastapi import APIRouter, Depends, Response
from src.database.repository.repo_auth import get_current_user
from src.web.resources.schemas.schemas_cards_sync import SyncShem
from src.database.repository.repo_cards import sync_cards_query

api_cards_v2 = APIRouter(prefix="/v2/cards", tags=["Карты"])


@api_cards_v2.post("/sync", summary="Синхранизация карты")
def sync_cards(response: Response, current_user: Depends(get_current_user)):
    result = sync_cards_query()
    response.status_code = result.result.get("code", 200)
    return result
