import uuid
from loguru import logger
from sqlalchemy import select, or_, update, delete, insert
from src.database.models.model_cards import Cards
from src.database.models.model_cards_access import CardsAccess
from src.database.db_engine import SessionLocal
from src.web.resources.responses import api_response, error_403, error_500


def sync_cards_query(requester, data):
    with SessionLocal() as session:
        changes_list = [item.model_dump(exclude_unset=True) for item in data.changes]
        stmt = insert(Cards).values(changes_list)
        upsert_stmt = stmt.on_conflict_do_update()
        if not changes_list:
            return api_response(True, "Синхранизировать нечего")
        for item in data.changes:
            db_item = session.query(Cards).filter(Cards.id == item.id).first()
            if db_item:
                update_data = item.model_dump(exclude_unset=True, exclude={"id"})
                if item.data_update > db_item.date_update:
                    for key, value in update_data.items():
                        setattr(db_item, key, value)
            else:

                session.add

        session.commit()
