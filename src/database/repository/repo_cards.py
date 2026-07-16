from loguru import logger
from time import time
from sqlalchemy import select, or_, update, delete, insert
from database.models.model_cards import Cards, CardsAccess
from database.models.model_users import Users
from database.db_connect import AsyncSessionLocal
from web.resources.responses import api_response, error_403, error_404, error_500


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
                    has_write_access = False
                    if db_card.own_login != requester.login and not requester.is_admin:
                        access_res = await session.execute(
                            select(CardsAccess).where(
                                CardsAccess.card_id == db_card.id,
                                CardsAccess.user_login == requester.login,
                                CardsAccess.access_type == "write",
                            )
                        )
                        if access_res.scalar_or_none():
                            has_write_access = True
                    else:
                        has_write_access = True
                    if not has_write_access:
                        logger.warning(
                            f"Пользователь {requester.login} пытался перезаписать чужую карту {db_card.id} без прав 'write'"
                        )
                        continue
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
                select(
                    Cards.id,
                    Cards.name,
                    Cards.about,
                    Cards.own_login,
                    Cards.version,
                    Cards.is_delete,
                    Cards.code,
                    Cards.code_type,
                )
                .outerjoin(CardsAccess, Cards.id == CardsAccess.card_id)
                .where(
                    Cards.version > since_version,
                    or_(
                        Cards.own_login == requester.login,
                        CardsAccess.user_login == requester.login,
                    ),
                )
                .order_by(Cards.version.asc())
                .distinct()
                .limit(limit + 1)
            )
            cards_models = [dict(row) for row in cards_models_query.mappings().all()]
            has_more = len(cards_models) > limit
            if has_more:
                cards_models = cards_models[:limit]
            current_server_version = since_version
            if cards_models:
                current_server_version = cards_models[-1]["version"]
            return api_response(
                True,
                "Список карт получен",
                cards=cards_models,
                version=current_server_version,
                has_more=has_more,
            )
    except Exception as err:
        logger.error(f"Ошибка при получении обновлений карт (downstream): {err}")
        raise error_500("Не удалось получить обновления карт")


async def grant_card_access_query(
    requester, card_id, target_login: str, access_type: str = "read"
):
    if access_type not in ["read", "write"]:
        return api_response(
            False, "Недопустимый тип прав. Используйте 'read' или 'write'", 400
        )
    async with AsyncSessionLocal() as session:
        try:
            card_result = await session.execute(
                select(Cards).where(Cards.id == card_id)
            )
            card = card_result.scalar_or_none()
            if not card:
                return error_404("Карта не найдена")
            if card.own_login != requester.login and not requester.is_admin:
                return error_403("У вас нет прав на раздачу доступа к этой карте")
            user_result = await session.execute(
                select(Users).where(Users.login == target_login)
            )
            if not user_result.scalar_or_none():
                return error_404(f"Пользователь с логином {target_login} не найден")
            access_result = await session.execute(
                select(CardsAccess).where(
                    CardsAccess.card_id == card_id,
                    CardsAccess.user_login == target_login,
                )
            )
            existing_access = access_result.scalar_or_none()
            if existing_access:
                if existing_access.access_type != access_type:
                    existing_access.access_type = access_type
                    card.version = int(time() * 1000)
                    await session.commit()
                    return api_response(
                        True,
                        f"Права пользователя {target_login} изменены на {access_type}",
                        200,
                    )
                return api_response(
                    False,
                    "Такой уровень доступа уже предоставлен этому пользователю",
                    400,
                )
            new_access = CardsAccess(
                card_id=card_id, user_login=target_login, access_type=access_type
            )
            card.version = int(time() * 1000)
            session.add(new_access)
            await session.commit()
            logger.success(
                f"Пользователь {requester.login} предоставил доступ к карте {card_id} для {target_login}"
            )
            return api_response(
                True,
                f"Доступ к карте успешно предоставлен пользователю {target_login}",
                201,
            )
        except Exception as err:
            await session.rollback()
            logger.exception(f"Ошибка при выдаче прав доступа к карте {card_id}: {err}")
            return error_500("Не удалось предоставить доступ к карте")


async def revoke_card_access_query(
    requester, card_id: int, target_login: str, access_type: str
):
    async with AsyncSessionLocal() as session:
        try:
            card_result = await session.execute(
                select(Cards).where(Cards.id == card_id)
            )
            card = card_result.scalar_or_none()
            if not card:
                return error_404("Карта не найдена")
            if card.own_login != requester.login and not requester.is_admin:
                return error_403("Вы не можете управлять доступом этой карты")
            access_result = await session.execute(
                select(CardsAccess).where(
                    CardsAccess.card_id == card_id,
                    CardsAccess.user_login == target_login,
                )
            )
            existing_access = access_result.scalar_or_none()
            if not existing_access:
                return error_404(
                    f"Права доступа для пользователя {target_login} не обнаружены"
                )
            if access_type == "write":
                if existing_access.access_type == "read":
                    return api_response(
                        False,
                        f"У пользователя {target_login} и так нет прав на запись",
                        400,
                    )
                existing_access.access_type = "read"
                msg = f"Права пользователя {target_login} понижены до 'только чтение'"
            else:
                result = await session.execute(
                    delete(CardsAccess).where(
                        CardsAccess.card_id == card_id,
                        CardsAccess.user_login == target_login,
                    )
                )
                if result.rowcount == 0:
                    return error_404("Права доступа для этого пользователя не найдены")
            card.version = int(time() * 1000)
            await session.commit()
            logger.success(
                f"Пользователь {requester.login} отозвал доступ к карте {card_id} у {target_login}"
            )
            return api_response(
                True, f"Доступ для пользователя {target_login} успешно отозван", 200
            )
        except Exception as err:
            await session.rollback()
            logger.exception(f"Ошибка при отзыве прав доступа: {err}")
            return error_500("Не удалось отозвать доступ")
