from fastapi import APIRouter, Depends, Response, Body
from web.resources.schemas.schemas_cards_sync import UpstreamSyncShem
from web.api.api_auth import get_current_user
from database.repository.repo_cards import (
    sync_upstream_query,
    sync_downstream_query,
    grant_card_access_query,
    revoke_card_access_query,
)

api_cards = APIRouter(prefix="/cards", tags=["Карты"])


@api_cards.post("/sync/upstream", summary="Синхранизация карт с клиента")
async def sync_upstream(
    sync_cards: UpstreamSyncShem,
    response: Response,
    current_user=Depends(get_current_user),
):
    result = await sync_upstream_query(requester=current_user, data=sync_cards)
    response.status_code = result.get("code", 201)
    return result


@api_cards.get("/sync/downstream", summary="Синхранизация карт с сервера")
async def sync_downstream(
    last_version: int, response: Response, current_user=Depends(get_current_user)
):
    result = await sync_downstream_query(
        requester=current_user, since_version=last_version
    )
    response.status_code = result.get("code", 200)
    return result


@api_cards.post("/share", summary="Поделиться картой / Выдать права")
async def share_card(
    card_id: int = Body(..., description="ID дисконтной карты"),
    target_login: str = Body(
        ..., embed=True, description="Логин пользователя, которому даем доступ"
    ),
    access_type: str = Body("read", description="Тип прав: 'read' или 'write'"),
    current_user=Depends(get_current_user),
):
    return await grant_card_access_query(
        requester=current_user,
        card_id=card_id,
        target_login=target_login,
        access_type=access_type,
    )


# Эндпоинт для отзыва прав
@api_cards.delete("/share", summary="Отозвать доступ к карте")
async def unshare_card(
    card_id: int = Body(..., description="ID дисконтной карты"),
    target_login: str = Body(
        ..., embed=True, description="Логин пользователя, у котрого забираем доступ"
    ),
    access_type: str = Body("read", description="Тип прав: 'read' или 'write'"),
    current_user=Depends(get_current_user),
):
    return await revoke_card_access_query(
        requester=current_user,
        card_id=card_id,
        target_login=target_login,
        access_type=access_type,
    )
