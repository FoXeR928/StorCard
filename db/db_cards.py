import os
from loguru import logger
from fastapi import HTTPException, status
from sqlalchemy import select, delete, update
from typing import Optional

from db.db_create import session_create, Cards, CardsAccess, Users
from core.config import MEDIA_DIR
from core.schemas import UserSchema


class CardRepository:
    """
    Объединенный репозиторий для управления дисконтными картами и уровнями доступа.
    Инкапсулирует всю бизнес-логику СУБД в одном месте.
    """

    @staticmethod
    async def _verify_access(
        session, card_id: str, user_id: str, allowed_levels: list, is_admin: bool
    ) -> str:
        """Внутренний метод для быстрой централизованной проверки прав доступа."""
        if is_admin:
            return "admin"

        access_level = (
            await session.scalars(
                select(CardsAccess.access_level).where(
                    CardsAccess.card_id == card_id, CardsAccess.user_id == user_id
                )
            )
        ).one_or_none()

        if not access_level or (allowed_levels and access_level not in allowed_levels):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на выполнение этого действия с данной картой.",
            )
        return access_level

    @classmethod
    async def get_cards(
        cls, current_user: UserSchema, global_view: bool = False
    ) -> list:
        """Объединенный метод получения карт: возвращает либо личные карты, либо ВСЕ (для админа)."""
        async with session_create() as session:
            stmt = select(Cards.id, Cards.name, Cards.about, Cards.barcode)

            if global_view:
                if not current_user.is_admin:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Недостаточно прав.",
                    )
                logger.debug(
                    f"Администратор {current_user.login} запросил глобальный список карт."
                )
            else:
                stmt = stmt.join(CardsAccess, CardsAccess.card_id == Cards.id).where(
                    CardsAccess.user_id == current_user.id
                )
                logger.debug(
                    f"Пользователь {current_user.login} запросил список своих карт."
                )

            return [dict(row._mapping) for row in (await session.execute(stmt)).all()]

    @classmethod
    async def get_card_detail(cls, card_id: str, current_user: UserSchema) -> dict:
        """Детальная информация о конкретной карте."""
        async with session_create() as session:
            access_level = await cls._verify_access(
                session, card_id, current_user.id, [], current_user.is_admin
            )
            card = (
                await session.execute(
                    select(
                        Cards.id,
                        Cards.name,
                        Cards.about,
                        Cards.barcode,
                        Cards.image_path,
                    ).where(Cards.id == card_id)
                )
            ).one_or_none()
            if not card:
                raise HTTPException(
                    status_code=404, detail="Дисконтная карта не найдена."
                )
            result = dict(card._mapping)
            result["my_access_level"] = access_level
            return result

    @classmethod
    async def add_card(
        cls,
        name: str,
        about: str,
        barcode: str,
        current_user: UserSchema,
        image_path: Optional[str] = None,
    ) -> dict:
        """Создание новой карты с автоматическим назначением прав 'owner'."""
        async with session_create() as session:
            try:
                new_card = Cards(
                    name=name, about=about, barcode=barcode, image_path=image_path
                )
                session.add(new_card)
                await session.flush()  # Извлекаем UUID до коммита

                session.add(
                    CardsAccess(
                        user_id=current_user.id,
                        card_id=new_card.id,
                        access_level="owner",
                    )
                )
                await session.commit()

                logger.success(
                    f"Пользователь {current_user.login} создал карту {new_card.id}"
                )
                return {
                    "result": True,
                    "card_id": new_card.id,
                    "message": "Карта успешно создана.",
                }
            except Exception as err:
                logger.error(f"Ошибка создания карты: {err}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Ошибка сервера.",
                )

    @classmethod
    async def share_card_access(
        cls,
        card_id: str,
        target_login: str,
        access_level: str,
        current_user: UserSchema,
    ) -> dict:
        """Предоставление доступа к карте другому пользователю (шеринг)."""
        if access_level not in ["editor", "viewer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недопустимый уровень доступа.",
            )

        async with session_create() as session:
            card_exists = (
                await session.scalars(select(Cards).where(Cards.id == card_id))
            ).one_or_none()
            if not card_exists:
                raise HTTPException(
                    status_code=404, detail="Дисконтная карта не найдена."
                )

            await cls._verify_access(
                session,
                card_id,
                current_user.id,
                ["owner"],
                current_user.is_admin,
            )

            target_user = (
                await session.scalars(select(Users).where(Users.login == target_login))
            ).one_or_none()
            if not target_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден.",
                )

            already_has_access = (
                await session.scalars(
                    select(CardsAccess).where(
                        CardsAccess.card_id == card_id,
                        CardsAccess.user_id == target_user.id,
                    )
                )
            ).one_or_none()
            if already_has_access:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Доступ уже предоставлен.",
                )

            session.add(
                CardsAccess(
                    user_id=target_user.id, card_id=card_id, access_level=access_level
                )
            )
            await session.commit()

            logger.success(
                f"Юзер {current_user.login} поделился картой {card_id} с {target_login} ({access_level})"
            )
            return {
                "result": True,
                "message": f"Доступ успешно предоставлен пользователю {target_login}.",
            }

    @classmethod
    async def update_card(
        cls, card_id: str, update_data: dict, current_user: UserSchema
    ) -> dict:
        """
        УНИВЕРСАЛЬНЫЙ МЕТОД ОБНОВЛЕНИЯ ДАННЫХ КАРТЫ.
        Объединяет в себе обновление имени, описания, штрихкода и изображения.
        """
        ALLOWED = {"name", "about", "barcode", "image_path"}
        filtered_data = {k: v for k, v in update_data.items() if k in ALLOWED}

        if not filtered_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления.",
            )

        async with session_create() as session:
            await cls._verify_access(
                session,
                card_id,
                current_user.id,
                ["owner", "editor"],
                current_user.is_admin,
            )

            card_exists = (
                await session.scalars(select(Cards).where(Cards.id == card_id))
            ).one_or_none()
            if not card_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Дисконтная карта не найдена.",
                )

            try:
                await session.execute(
                    update(Cards).where(Cards.id == card_id).values(**filtered_data)
                )
                await session.commit()
                logger.success(
                    f"Пользователь {current_user.login} обновил параметры {list(filtered_data.keys())} карты {card_id}"
                )
                return {
                    "result": True,
                    "message": "Информация о карте успешно обновлена.",
                }
            except Exception as err:
                logger.error(f"Не удалось обновить карту {card_id}. Ошибка: {err}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Ошибка обновления карты.",
                )

    @classmethod
    async def change_card_owner(
        cls, card_id: str, target_login: str, current_user: UserSchema
    ) -> dict:
        """
        ПЕРЕДАЧА ПРАВ ВЛАДЕЛЬЦА (Вместо старого update_card_own_query).
        Переводит текущего владельца в статус 'editor', а новому выдает статус 'owner'.
        """
        async with session_create() as session:
            card_exists = (
                await session.scalars(select(Cards).where(Cards.id == card_id))
            ).one_or_none()
            if not card_exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Дисконтная карта не найдена.",
                )

            await cls._verify_access(
                session, card_id, current_user.id, ["owner"], current_user.is_admin
            )

            target_user = (
                await session.scalars(select(Users).where(Users.login == target_login))
            ).one_or_none()
            if not target_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь {target_login} не найден.",
                )
            current_owner_access = (
                await session.scalars(
                    select(CardsAccess).where(
                        CardsAccess.card_id == card_id,
                        CardsAccess.access_level == "owner",
                    )
                )
            ).one_or_none()
            if current_owner_access and current_owner_access.user_id == target_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь уже является владельцем карты.",
                )
            try:
                if current_owner_access:
                    current_owner_access.access_level = "editor"
                existing_access = (
                    await session.scalars(
                        select(CardsAccess).where(
                            CardsAccess.card_id == card_id,
                            CardsAccess.user_id == target_user.id,
                        )
                    )
                ).one_or_none()

                if existing_access:
                    existing_access.access_level = "owner"
                else:
                    session.add(
                        CardsAccess(
                            user_id=target_user.id,
                            card_id=card_id,
                            access_level="owner",
                        )
                    )

                await session.commit()
                logger.success(
                    f"Права владельца карты {card_id} успешно переданы пользователю {target_login}"
                )
                return {
                    "result": True,
                    "message": f"Права владельца успешно переданы пользователю {target_login}.",
                }
            except Exception as err:
                logger.error(
                    f"Ошибка при передаче прав владельца карты {card_id}: {err}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Ошибка смены владельца.",
                )

    @classmethod
    async def delete_card(cls, card_id, current_user):
        async with session_create() as session:
            card = (
                await session.scalars(select(Cards).where(Cards.id == card_id))
            ).one_or_none()
            if not card:
                raise HTTPException(
                    status_code=404, detail="Дисконтная карта не найдена."
                )

            await cls._verify_access(
                session, card_id, current_user.id, ["owner"], current_user.is_admin
            )
            image_path = card.image_path

            try:
                await session.execute(
                    delete(CardsAccess).where(CardsAccess.card_id == card_id)
                )
                await session.execute(delete(Cards).where(Cards.id == card_id))
                await session.commit()
            except Exception as err:
                await session.rollback()
                logger.error(f"Ошибка удаления карты {card_id}: {err}")
                raise HTTPException(status_code=500, detail="Ошибка удаления карты.")

            # После успешного удаления из БД — чистим файл
            if image_path:
                file_path = MEDIA_DIR.parent / image_path
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        logger.info(f"Удалён файл изображения {file_path}")
                except Exception as err:
                    logger.warning(
                        f"Не удалось удалить файл изображения {file_path}: {err}"
                    )

            logger.success(f"Пользователь {current_user.login} удалил карту {card_id}")
            return {"result": True, "message": "Дисконтная карта успешно удалена."}
