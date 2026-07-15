from loguru import logger
from time import time
from sqlalchemy import select, or_, update, delete, insert
from database.models.model_cards import Cards, CardsAccess
from database.db_connect import SessionLocal
from web.resources.responses import api_response, error_403, error_500


def sync_upstream_query(requester, data):
    if not data.changes:
        return api_response(True, "Нет изменений для загрузки", 201)
    try:
        incoming_ids = [item.id for item in data.changes]
        with SessionLocal() as session:
            existing_cards  = session.execute(select(Cards).where(Cards.id.in_(incoming_ids))).mappings().all()
            next_server_version = int(time.time() * 1000)
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
                        name=update_data.get("name")
                        about=update_data.get("about"),
                        own_login=requester.login,
                        version=next_server_version,
                        is_delete=update_data.get("is_delete", False),
                        code=update_data.get("code", ""),
                        code_type=update_data.get("code_type", "")
                    )
                    session.add(new_card)
            session.commit()
            return api_response(True,"Данные карт обновлены",201)
    except Exception as e:
        raise  error_500("Не удалось загрузить карты")


def sync_downstream_query(requester,since_version=0,limit=50):
    if since_version != 0 and since_version < (time * 1000):