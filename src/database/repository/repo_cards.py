import uuid
from loguru import logger
from sqlalchemy import select, or_, update, delete
from src.database.models.model_cards import Cards
from src.database.models.model_cards_access import CardsAccess
import src.database.engine as engine
from src.core.responses import api_response, error_404, error_403, error_500


def get_card_query(card_id: uuid.UUID, user):
    with engine.SessionLocal() as session:
        stmt = (
            select(Cards)
            .outerjoin(CardsAccess)
            .where(
                Cards.id == card_id,
                or_(
                    Cards.own_login == user.login,
                    CardsAccess.user_login == user.login,
                    user.is_admin == True,
                ),
            )
        )
        card = session.scalar(stmt)
        if not card:
            exists = session.get(Cards, card_id)
            return error_404("Карта не найдена") if not exists else error_403()
        return api_response(
            True,
            "Карта получена",
            card={
                "id": str(card.id),
                "name": card.name,
                "about": card.about,
                "code": card.code,
                "code_type": card.code_type,
                "owner": card.own_login,
            },
        )


def add_card_access_query(card_id: uuid.UUID, login: str, user):
    with engine.SessionLocal() as session:
        # Проверяем, что ТЫ владелец, прежде чем давать доступ другому
        card = session.scalar(
            select(Cards).where(Cards.id == card_id, Cards.own_login == user.login)
        )
        if not card and not user.is_admin:
            return error_403("Только владелец может раздавать доступ")

        try:
            session.add(CardsAccess(user_login=login, card_id=card_id))
            session.commit()
            return api_response(True, f"Доступ для {login} добавлен", code=201)
        except Exception:
            return api_response(
                False, "Доступ уже существует или юзер не найден", code=400
            )


def user_cards_query(user):
    with engine.SessionLocal() as session:
        try:
            stmt = (
                select(Cards.id, Cards.name, Cards.own_login)
                .outerjoin(CardsAccess)
                .where(
                    or_(
                        Cards.own_login == user.login,
                        CardsAccess.user_login == user.login,
                    )
                )
                .distinct()
            )
            cards = session.execute(stmt).mappings().all()
            result = [
                {"id": str(c.id), "name": c.name, "owner": c.own_login} for c in cards
            ]
            return api_response(True, "Список карт пользователя получен", cards=result)
        except Exception as err:
            logger.error(f"Ошибка получения карт пользователя: {err}")
            return error_500()


def all_cards_query():
    with engine.SessionLocal() as session:
        try:
            stmt = select(Cards.id, Cards.name, Cards.own_login)
            cards = session.execute(stmt).mappings().all()
            result = [
                {"id": str(c.id), "name": c.name, "owner": c.own_login} for c in cards
            ]
            return api_response(True, "Все карты получены", cards=result)
        except Exception as err:
            logger.error(f"Ошибка получения всех карт: {err}")
            return error_500()


def add_card_query(name: str, about: str, user, code: str, code_type: str):
    with engine.SessionLocal() as session:
        try:
            new_card = Cards(
                name=name,
                about=about,
                own_login=user.login,
                code=code,
                code_type=code_type,
            )
            session.add(new_card)
            session.flush()
            access = CardsAccess(user_login=user.login, card_id=new_card.id)
            session.add(access)

            session.commit()
            return api_response(True, "Карта добавлена", code=201, id=str(new_card.id))
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка БД при добавлении: {err}")
            return error_500()


def update_card_field(id: uuid.UUID, user, **values):
    with engine.SessionLocal() as session:
        try:
            stmt = (
                update(Cards)
                .where(
                    Cards.id == id,
                    or_(Cards.own_login == user.login, user.is_admin),
                )
                .values(**values, version=Cards.version + 1)
            )

            result = session.execute(stmt)
            session.commit()

            if result.rowcount == 0:
                return error_403("Нет прав или карта не найдена")
            return api_response(True, "Данные обновлены",201)
        except Exception as err:
            logger.error(f"Ошибка обновления {values}: {err}")
            return error_500()


def delete_card_query(card_id: uuid.UUID, user):
    with engine.SessionLocal() as session:
        try:
            stmt = delete(Cards).where(
                Cards.id == card_id,
                or_(Cards.own_login == user.login, user.is_admin == True),
            )
            result = session.execute(stmt)
            session.commit()
            if result.rowcount == 0:
                return error_403()
            return api_response(True, "Карта и доступы удалены")
        except Exception as err:
            logger.error(f"Ошибка удаления: {err}")
            return error_500()
