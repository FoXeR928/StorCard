from loguru import logger
from time import time
from sqlalchemy import select, or_, update, delete, insert
from database.models.model_cards import Cards, CardsAccess
from database.db_connect import AsyncSessionLocal
from web.resources.responses import api_response, error_403, error_500


async def sync_upstream_query(requester, data):
    if not data.changes:
        return api_response(True, "Нет изменений для загрузки", 201)
    try:
        incoming_ids = [item.id for item in data.changes]
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Cards).where(Cards.id.in_(incoming_ids))
            )
            existing_cards = {card.id: card for card in result.scalars().all()}
            next_server_version = int(time() * 1000)
            for item in data.changes:
                update_data = item.model_dump(exclude_unset=True)
                update_data.pop("id", None)
                update_data.pop("version", None)
                if item.id in existing_cards:
                    db_card = existing_cards[item.id]
                    if item.version >= db_card.version:
                        for key, value in update_data.items():
                            setattr(db_card, key, value)
                        db_card.version = next_server_version
                else:
                    new_card = Cards(
                        id=item.id,
                        name=update_data.get("name"),
                        about=update_data.get("about"),
                        own_login=requester.login,
                        version=next_server_version,
                        is_delete=update_data.get("is_delete", False),
                        code=update_data.get("code"),
                        code_type=update_data.get("code_type"),
                    )
                    session.add(new_card)
            await session.commit()
            return api_response(True, "Данные карт обновлены", 201)
    except Exception as err:
        await session.rollback()
        logger.error(f"Ошибка при синхронизации карт (upstream): {err}")
        return error_500("Не удалось загрузить карты")


async def sync_downstream_query(requester, since_version=0, limit=50):
    try:
        async with AsyncSessionLocal() as session:
            cards_models_query = await session.execute(
                select(Cards)
                .outerjoin(CardsAccess, Cards.id == CardsAccess.card_id)
                .where(
                    Cards.version > since_version,
                    or_(
                        Cards.own_login == requester.login,
                        CardsAccess.user_login == requester.login,
                    ),
                )
                .order_by(Cards.version.asc())
                .limit(limit + 1)
            )
            cards_models = cards_models_query.scalars().all()
            has_more = len(cards_models) > limit
            if has_more:
                cards_models = cards_models[:limit]
            current_server_version = since_version
            if cards_models:
                current_server_version = cards_models[-1].version
            return api_response(
                True,
                "Список карт получен",
                cards=cards_models,
                version=current_server_version,
                has_more=has_more,
            )
    except Exception as err:
        logger.error(f"Ошибка при получении обновлений карт (downstream): {err}")
        return error_500("Не удалось получить обновления карт")
