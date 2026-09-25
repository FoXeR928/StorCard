import os
from loguru import logger
from fastapi import HTTPException, status
from sqlalchemy import select, delete, update

from db.db_create import session_create, Cards, CardsAccess, Users
from api.api_auth import UserSchema


class CardRepository:
    """
    Объединенный репозиторий для управления дисконтными картами и уровнями доступа.
    Инкапсулирует всю бизнес-логику СУБД в одном месте.
    """

    @staticmethod
    def _verify_access(session, card_id: str, user_id: str, allowed_levels: list, is_admin: bool) -> str:
        """Внутренний метод для быстрой централизованной проверки прав доступа."""
        if is_admin:
            return "admin"
            
        access_level = session.scalars(
            select(CardsAccess.access_level)
            .where(CardsAccess.card_id == card_id, CardsAccess.user_id == user_id)
        ).one_or_none()

        if not access_level or (allowed_levels and access_level not in allowed_levels):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на выполнение этого действия с данной картой."
            )
        return access_level

    @classmethod
    def get_cards(cls, current_user: UserSchema, global_view: bool = False) -> list:
        """Объединенный метод получения карт: возвращает либо личные карты, либо ВСЕ (для админа)."""
        with session_create() as session:
            stmt = select(Cards.id, Cards.name, Cards.about, Cards.barcode)
            
            if global_view:
                if not current_user.is_admin:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав.")
                logger.debug(f"Администратор {current_user.login} запросил глобальный список карт.")
            else:
                stmt = stmt.join(CardsAccess, CardsAccess.card_id == Cards.id).where(CardsAccess.user_id == current_user.id)
                logger.debug(f"Пользователь {current_user.login} запросил список своих карт.")
                
            return [dict(row._mapping) for row in session.execute(stmt).all()]

    @classmethod
    def get_card_detail(cls, card_id: str, current_user: UserSchema) -> dict:
        """Детальная информация о конкретной карте."""
        with session_create() as session:
            access_level = cls._verify_access(session, card_id, current_user.id, [], current_user.is_admin)
            
            card = session.execute(
                select(Cards.id, Cards.name, Cards.about, Cards.barcode, Cards.image_path).where(Cards.id == card_id)
            ).one_or_none()
            
            if not card:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисконтная карта не найдена.")
                
            result = dict(card._mapping)
            result["my_access_level"] = access_level
            return result

    @classmethod
    def add_card(cls, name: str, about: str, barcode: str, current_user: UserSchema, image_path: str = None) -> dict:
        """Создание новой карты с автоматическим назначением прав 'owner'."""
        with session_create() as session:
            try:
                new_card = Cards(name=name, about=about, barcode=barcode, image_path=image_path)
                session.add(new_card)
                session.flush() # Извлекаем UUID до коммита

                session.add(CardsAccess(user_id=current_user.id, card_id=new_card.id, access_level="owner"))
                session.commit()
                
                logger.success(f"Пользователь {current_user.login} создал карту {new_card.id}")
                return {"result": True, "card_id": new_card.id, "message": "Карта успешно создана."}
            except Exception as err:
                logger.error(f"Ошибка создания карты: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка сервера.")

    @classmethod
    def share_card_access(cls, card_id: str, target_login: str, access_level: str, current_user: UserSchema) -> dict:
        """Предоставление доступа к карте другому пользователю (шеринг)."""
        if access_level not in ["editor", "viewer"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Недопустимый уровень доступа.")

        with session_create() as session:
            cls._verify_access(session, card_id, current_user.id, ["owner"], current_user.is_admin)
            
            target_user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
            if not target_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")

            already_has_access = session.scalars(
                select(CardsAccess).where(CardsAccess.card_id == card_id, CardsAccess.user_id == target_user.id)
            ).one_or_none()
            if already_has_access:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Доступ уже предоставлен.")

            session.add(CardsAccess(user_id=target_user.id, card_id=card_id, access_level=access_level))
            session.commit()
            
            logger.success(f"Юзер {current_user.login} поделился картой {card_id} с {target_login} ({access_level})")
            return {"result": True, "message": f"Доступ успешно предоставлен пользователю {target_login}."}


    @classmethod
    def update_card(cls, card_id: str, update_data: dict, current_user: UserSchema) -> dict:
        """
        УНИВЕРСАЛЬНЫЙ МЕТОД ОБНОВЛЕНИЯ ДАННЫХ КАРТЫ.
        Объединяет в себе обновление имени, описания, штрихкода и изображения.
        """
        filtered_data = {k: v for k, v in update_data.items() if v is not None and k in ["name", "about", "barcode", "image_path"]}
        
        if not filtered_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет данных для обновления.")

        with session_create() as session:
            cls._verify_access(session, card_id, current_user.id, ["owner", "editor"], current_user.is_admin)

            card_exists = session.scalars(select(Cards).where(Cards.id == card_id)).one_or_none()
            if not card_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисконтная карта не найдена.")

            try:
                session.execute(
                    update(Cards).where(Cards.id == card_id).values(**filtered_data)
                )
                session.commit()
                logger.success(f"Пользователь {current_user.login} обновил параметры {list(filtered_data.keys())} карты {card_id}")
                return {"result": True, "message": "Информация о карте успешно обновлена."}
            except Exception as err:
                logger.error(f"Не удалось обновить карту {card_id}. Ошибка: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка обновления карты.")

    @classmethod
    def change_card_owner(cls, card_id: str, target_login: str, current_user: UserSchema) -> dict:
        """
        ПЕРЕДАЧА ПРАВ ВЛАДЕЛЬЦА (Вместо старого update_card_own_query).
        Переводит текущего владельца в статус 'editor', а новому выдает статус 'owner'.
        """
        with session_create() as session:
            cls._verify_access(session, card_id, current_user.id, ["owner"], current_user.is_admin)

            target_user = session.scalars(select(Users).where(Users.login == target_login)).one_or_none()
            if not target_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Пользователь {target_login} не найден.")

            try:
                session.execute(
                    update(CardsAccess)
                    .where(CardsAccess.card_id == card_id, CardsAccess.user_id == current_user.id)
                    .values(access_level="editor")
                )

                existing_access = session.scalars(
                    select(CardsAccess).where(CardsAccess.card_id == card_id, CardsAccess.user_id == target_user.id)
                ).one_or_none()

                if existing_access:
                    existing_access.access_level = "owner"
                else:
                    session.add(CardsAccess(user_id=target_user.id, card_id=card_id, access_level="owner"))

                session.commit()
                logger.success(f"Права владельца карты {card_id} успешно переданы пользователю {target_login}")
                return {"result": True, "message": f"Права владельца успешно переданы пользователю {target_login}."}
            except Exception as err:
                logger.error(f"Ошибка при передаче прав владельца карты {card_id}: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка смены владельца.")

    @classmethod
    def delete_card(cls, card_id: str, current_user: UserSchema) -> dict:
        """
        ПОЛНОЕ УДАЛЕНИЕ КАРТЫ И ВСЕХ СВЯЗАННЫХ С НЕЙ ПРАВ ДОСТУПА.
        """
        with session_create() as session:
            cls._verify_access(session, card_id, current_user.id, ["owner"], current_user.is_admin)

            card_exists = session.scalars(select(Cards).where(Cards.id == card_id)).one_or_none()
            if not card_exists:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Дисконтная карта не найдена.")

            try:
                session.execute(delete(Cards).where(Cards.id == card_id))
                session.execute(delete(CardsAccess).where(CardsAccess.card_id == card_id))
                session.commit()
                
                logger.success(f"Пользователь {current_user.login} полностью удалил карту {card_id}")
                return {"result": True, "message": "Дисконтная карта успешно удалена из системы."}
            except Exception as err:
                logger.error(f"Ошибка удаления карты {card_id}: {err}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка удаления карты.")