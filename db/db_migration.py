from typing import Optional

from loguru import logger
from sqlalchemy import select

from db.db_create import session_create, Users, Cards, CardsAccess

MIGRATION_VERSION = 1
DEFAULT_IMPORT_PASSWORD = "storcard_import"


class MigrationRepository:
    """Единая точка входа для экспорта и импорта данных миграции."""

    # ----------------------------- EXPORT ----------------------------- #

    @classmethod
    async def export_all(cls) -> dict:
        async with session_create() as session:
            users = await cls._export_users(session)
            cards = await cls._export_cards(session)

        logger.info(
            f"Экспорт миграции: {len(users)} пользователей, {len(cards)} карт."
        )
        return {
            "version": MIGRATION_VERSION,
            "users": users,
            "cards": cards,
        }

    @staticmethod
    async def _export_users(session) -> list:
        rows = (
            await session.execute(
                select(
                    Users.login,
                    Users.user_name,
                    Users.is_admin,
                    Users.disabled,
                    Users.password_hash,
                )
            )
        ).all()
        return [dict(r._mapping) for r in rows]

    @staticmethod
    async def _export_cards(session) -> list:
        # Владельца берём из CardsAccess — это единственный источник истины.
        rows = (
            await session.execute(
                select(
                    Cards.name,
                    Cards.about,
                    Cards.barcode,
                    Users.login.label("owner_login"),
                )
                .join(CardsAccess, CardsAccess.card_id == Cards.id)
                .join(Users, Users.id == CardsAccess.user_id)
                .where(CardsAccess.access_level == "owner")
            )
        ).all()
        return [dict(r._mapping) for r in rows]

    # ----------------------------- IMPORT ----------------------------- #

    @classmethod
    async def import_data(cls, data: dict) -> dict:
        users_data = data.get("users") or []
        cards_data = data.get("cards") or []

        stats = {
            "users_imported": 0,
            "users_updated": 0,
            "cards_imported": 0,
            "cards_skipped": 0,
        }

        async with session_create() as session:
            try:
                await cls._import_users(session, users_data, stats)
                await session.flush()  # нужны id для FK карт
                await cls._import_cards(session, cards_data, stats)
                await session.commit()
            except Exception as err:
                await session.rollback()
                logger.exception(f"Импорт миграции отменён: {err}")
                raise

        logger.success(
            f"Миграция: +{stats['users_imported']} users "
            f"(~{stats['users_updated']} updated), "
            f"+{stats['cards_imported']} cards, "
            f"skipped {stats['cards_skipped']}."
        )
        return {"result": True, **stats}

    @staticmethod
    async def _import_users(session, users_data: list, stats: dict) -> None:
        for u in users_data:
            login = u.get("login")
            if not login:
                continue

            existing = (
                await session.scalars(
                    select(Users).where(Users.login == login)
                )
            ).one_or_none()

            if existing:
                existing.is_admin = bool(u.get("is_admin", existing.is_admin))
                if "disabled" in u:
                    existing.disabled = bool(u["disabled"])
                if u.get("password_hash"):
                    existing.password_hash = u["password_hash"]
                stats["users_updated"] += 1
                continue

            new_user = Users(
                login=login,
                user_name=u.get("user_name", login),
                is_admin=bool(u.get("is_admin", False)),
                disabled=bool(u.get("disabled", False)),
            )
            if u.get("password_hash"):
                new_user.password_hash = u["password_hash"]
            else:
                # Старый/битый формат — не роняем импорт, ставим временный пароль.
                new_user.set_password(DEFAULT_IMPORT_PASSWORD)
                logger.warning(
                    f"У {login} нет password_hash — установлен "
                    f"пароль '{DEFAULT_IMPORT_PASSWORD}'."
                )

            session.add(new_user)
            stats["users_imported"] += 1

    @classmethod
    async def _import_cards(cls, session, cards_data: list, stats: dict) -> None:
        for c in cards_data:
            barcode = c.get("barcode")
            if not barcode:
                continue

            # Идемпотентность: не плодим дубликаты при повторном импорте.
            duplicate = (
                await session.scalars(
                    select(Cards.id).where(Cards.barcode == barcode)
                )
            ).first()
            if duplicate:
                stats["cards_skipped"] += 1
                continue

            owner = await cls._resolve_owner(session, c.get("owner_login"))
            if owner is None:
                logger.warning(
                    f"Карта '{barcode}' пропущена: владелец не найден "
                    f"и в БД нет ни одного активного администратора."
                )
                stats["cards_skipped"] += 1
                continue

            card = Cards(
                name=c.get("name") or "Без названия",
                barcode=barcode,
                about=c.get("about"),
            )
            session.add(card)
            await session.flush()

            session.add(
                CardsAccess(
                    user_id=owner.id,
                    card_id=card.id,
                    access_level="owner",
                )
            )
            stats["cards_imported"] += 1

    @staticmethod
    async def _resolve_owner(session, owner_login: Optional[str]) -> Optional[Users]:
        """Владелец из файла → иначе самый старый активный админ."""
        if owner_login:
            owner = (
                await session.scalars(
                    select(Users).where(Users.login == owner_login)
                )
            ).one_or_none()
            if owner:
                return owner

        return (
            await session.scalars(
                select(Users)
                .where(Users.is_admin == True, Users.disabled == False)
                .order_by(Users.date_create)
                .limit(1)
            )
        ).first()