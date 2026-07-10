


def check_card_permission(session, card_id, user):
    card = session.scalar(select(Cards).where(Cards.id == card_id))
    if not card:
        return None, "Карта не найдена", 404
    if card.own_login != user.login and not user.is_admin:
        return None, "Только владелец может редактировать или раздавать доступ", 403
    return card, None


def cards_query(requester):
    with engine.SessionLocal() as session:
        try:
            stmt = (
                select(
                    Cards.id,
                    Cards.version,
                    Cards.name,
                    Cards.about,
                    Cards.code,
                    Cards.code_type,
                    Cards.own_login,
                )
                .outerjoin(CardsAccess)
                .where(
                    or_(
                        Cards.own_login == requester.login,
                        CardsAccess.user_login == requester.login,
                        requester.is_admin == True,
                    )
                )
                .distinct()
            )
            cards = session.execute(stmt).mappings().all()
            return api_response(True, "Список карт пользователя получен", cards=cards)
        except Exception as err:
            logger.error(f"Ошибка получения карт пользователя: {err}")
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


def update_card_query(id: uuid.UUID, user, **values):
    with engine.SessionLocal() as session:
        card, error_msg, code = check_card_permission(session, id, user)
        if not error_msg:
            return api_response(False, error_msg, code)
        try:
            if "access_login" in values:
                session.add(
                    CardsAccess(user_login=values.pop("access_login"), card_id=id)
                )
            session.execute(
                update(Cards)
                .where(
                    Cards.id == id,
                    or_(Cards.own_login == user.login, user.is_admin),
                )
                .values(**values, version=Cards.version + 1)
            )
            session.commit()
            return api_response(True, "Данные обновлены", 201)
        except Exception as err:
            session.rollback()
            logger.error(f"Ошибка обновления {values}: {err}")
            return error_500()


def delete_card_query(card_id: uuid.UUID, user):
    with engine.SessionLocal() as session:
        card, error_msg, code = check_card_permission(session, id, user)
        if not error_msg:
            return api_response(False, error_msg, code)
        try:
            stmt = delete(Cards).where(
                Cards.id == card_id,
                or_(Cards.own_login == user.login, user.is_admin == True),
            )
            result = session.execute(stmt)
            session.commit()
            return api_response(True, "Карта и доступы удалены")
        except Exception as err:
            logger.error(f"Ошибка удаления: {err}")
            return error_500()


def sync_cards_query(requester, data):
    with engine.SessionLocal() as session:
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
