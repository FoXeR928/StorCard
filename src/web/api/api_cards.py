from fastapi import APIRouter, Depends, Response
from web.resources.schemas.schemas_cards_sync import UpstreamSyncShem
from web.api.api_auth import get_current_user
from database.repository.repo_cards import sync_upstream_query, sync_downstream_query

api_cards = APIRouter(prefix="/cards", tags=["Синхранизация"])


@api_cards.post("/sync/upstream", summary="Синхранизация карт с клиента")
async def sync_upstream(
    sync_cards: UpstreamSyncShem, response: Response, current_user=Depends(get_current_user)
):
    result = sync_upstream_query(requester=current_user, data=sync_cards)
    response.status_code = result.result.get("code", 201)
    return result

@api_cards.get("/sync/downstream", summary="Синхранизация карт с сервера")
async def sync_downstream(
    last_version: int, response: Response, current_user=Depends(get_current_user)
):
    result = sync_downstream_query(requester=current_user,since_version=last_version)
    response.status_code = result.result.get("code", 200)
    return result