from sqlalchemy import select, update, delete
from loguru import logger

from db_modules.db_create import Cards, CardsAccess, session_create
from db_modules.db_query import check_user
from api.api_auth import User
from db_modules.db_answer import error_cards_get, error_access,error_card_not_found,error_card_code_generate,error_update_card,error_user_not_found


def check_card_access(card_id: int, user: User):
    if check_user(login=user.login) == True:
        if user.is_admin == False:
            try:
                session = session_create
                check_access = session.scalars(
                    select(CardsAccess.user_login).where(CardsAccess.card_id == card_id)
                ).one_or_none()
                if check_access == user.login:
                    result = True
                else:
                    result = False
            except Exception as err:
                logger.error(f"Ошибка сервера при проверки доступа к картам: {err}")
                result = False
            finally:
                session.close()
        else:
            result = True
    else:
        result = False
    return result


def check_card(card_id: int):
    try:
        session = session_create
        check_card_get = session.scalars(
            select(Cards).where(Cards.id == card_id)
        ).one_or_none()
        if check_card_get == None:
            result = False
        else:
            result = True
    except Exception as err:
        logger.error(f"Ошибка сервера при проверки карты: {err}")
        result = False
    finally:
        session.close()
    return result


def check_card_own(card_id: int, user: User):
    if check_user(login=user.login) == True:
        try:
            session = session_create
            check_own = session.scalars(
                select(Cards.own_login).where(Cards.id == card_id)
            ).one_or_none()
            if check_own == user.login or user.is_admin == True:
                result = True
            else:
                result = False
        except Exception as err:
            logger.error(f"Ошибка сервера при проверки владельца карты: {err}")
            result = False
        finally:
            session.close()
    else:
        result = False
    return result


def all_cards_query():
    try:
        session = session_create
        cards_get = session.execute(select(Cards.id, Cards.name, Cards.own_login)).all()
        cards = [row._mapping for row in cards_get]
        result = {
            "result": True,
            "message": "Карты получены",
            "cards": cards,
            "category": "success",
            "cod": 200,
        }
        logger.debug("Получение списка карт прошло успешно")
    except Exception as err:
        logger.error(f"Не удалось получить карты из базы Ошибка {err}")
        result = error_cards_get
    finally:
        session.close()
    return result


def user_cards_query(user: User):
    try:
        session = session_create
        cards_get = session.execute(
            select(Cards.id, Cards.name, Cards.about, Cards.own_login)
            .join(CardsAccess)
            .where(CardsAccess.user_login == user.login)
        ).all()
        cards = [row._mapping for row in cards_get]
        result = {
            "result": True,
            "message": "Карты получены",
            "cards": cards,
            "category": "success",
            "cod": 200,
        }
        logger.debug("Получение списка карт прошло успешно")
    except Exception as err:
        logger.error(f"Не удалось получить карты из базы Ошибка {err}")
        result = error_cards_get
    finally:
        session.close()
    return result


def get_card_query(card_id: int, user: User):
    if check_card(card_id=card_id) == True:
        if check_card_access(card_id=card_id, user=user) == True:
            try:
                session = session_create
                card_get = session.execute(
                    select(
                        Cards.id, Cards.name, Cards.about, Cards.code_svg,
                    ).where(Cards.id==card_id)
                ).one()
                card = card_get._mapping
                result = {
                    "result": True,
                    "message": "Карта получена",
                    "card": card,
                    "category": "success",
                    "cod": 200,
                }
                logger.debug("Получна карта прошло успешно")
            except Exception as err:
                logger.error(f"Не удалось получить карту из базы Ошибка {err}")
                result = {
                    "result": False,
                    "message": "Ошибка сервера не удалось получить информацию о карте",
                    "category": "error",
                    "cod": 500,
                }
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def add_card_query(name: str, about: str, user: User, code: str, code_type: str):
    try:
        session = session_create
        card_add = Cards(
            name=name, about=about, own_login=user.login, code_svg=code_svg
        )
        session.add(card_add)
        session.commit()
        session.flush()
        result = add_card_access_query(card_id=card_add.id, login=user.login, user=user)
        logger.success(f"Добавлена карта {card_add.id} пользователя {user.login}")
    except Exception as err:
        logger.error(f"Не удалось добавить карту Ошибка {err}")
        result = {
            "result": False,
            "message": "Ошибка сервера не удалось добавить карту",
            "category": "error",
            "cod": 500,
        }
    finally:
        session.close()
    return result


def add_card_access_query(card_id: int, login: str, user: User):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            try:
                session = session_create
                card_access = CardsAccess(user_login=login, card_id=card_id)
                session.add(card_access)
                session.commit()
                result = {
                    "result": True,
                    "message": "Добавлена карта",
                    "category": "success",
                    "cod": 201,
                }
                logger.success(
                    f"Добавлена доступ на карту {card_id} пользователю {login}"
                )
            except Exception as err:
                logger.error(f"Не удалось добавить доступ на карту Ошибка {err}")
                result = {
                    "result": False,
                    "message": "Ошибка сервера не удалось добавить карту",
                    "category": "error",
                    "cod": 500,
                }
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def update_card_name_query(card_id: int, user: User, name: str):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            try:
                session = session_create
                session.execute(
                    update(Cards).where(Cards.id == card_id).values(name=name)
                )
                session.commit()
                logger.debug("Имя карты обновлено успешно")
                result = {
                    "result": True,
                    "message": "Имя карты обновлено",
                    "category": "success",
                    "cod": 201,
                }
            except Exception as err:
                logger.error(f"Не удалось обновить информацию карты Ошибка {err}")
                result = error_update_card
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def update_card_about_query(card_id: int, user: User, about: str):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            try:
                session = session_create
                session.execute(
                    update(Cards).where(Cards.id == card_id).values(about=about)
                )
                session.commit()
                logger.debug("Описание карты обновлено успешно")
                result = {
                    "result": True,
                    "message": "Описание карты обновлено",
                    "category": "success",
                    "cod": 201,
                }
            except Exception as err:
                logger.error(f"Не удалось обновить инфомацию карты из базы Ошибка {err}")
                result = error_update_card
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def update_card_code_query(card_id: int, user: User, code: str, code_type: str):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            code_svg=check_code_type(code=code,code_type=code_type)
            if code_svg==None:
                result = error_card_code_generate
            else:
                try:
                    session = session_create
                    session.execute(
                        update(Cards)
                        .where(Cards.id == card_id)
                        .values(code=code, code_type=code_type)
                    )
                    session.commit()
                    logger.debug("Код карты обновлен успешно")
                    result = {
                        "result": True,
                        "message": "Код карты обновлен",
                        "category": "success",
                        "cod": 201,
                    }
                except Exception as err:
                    logger.error(f"Не удалось обновить информацию карты Ошибка {err}")
                    result = error_update_card
                finally:
                    session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def update_card_own_query(card_id: int, user: User, own: str):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            if check_user(login=own) == True:
                try:
                    session = session_create
                    session.execute(
                        update(Cards).where(Cards.id == card_id).values(own_login=own)
                    )
                    session.commit()
                    if check_card_access(card_id=card_id, user=user) == False:
                        add_card_access_query(
                            card_id=card_id, login=user.login, user=user
                        )
                    logger.success(
                        f"Владелец карты {card_id} обновлен на {own} успешно"
                    )
                    result = {
                        "result": True,
                        "message": "Владелец карты обновлен",
                        "category": "success",
                        "cod": 201,
                    }
                except Exception as err:
                    logger.error(f"Не удалось обновить информацию карты Ошибка {err}")
                    result = error_update_card
                finally:
                    session.close()
            else:
                result = error_user_not_found
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def update_card_image_query(card_id: int, user: User, image: str):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            try:
                session = session_create
                session.execute(
                    update(Cards).where(Cards.id == card_id).values(image=image)
                )
                session.commit()
                logger.debug("Изображение карты обновлено успешно")
                result = {
                    "result": True,
                    "message": "Изображение карты обновлено",
                    "category": "success",
                    "cod": 201,
                }
            except Exception as err:
                logger.error(f"Не удалось обновить информацию карты Ошибка {err}")
                result = error_update_card
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result


def delete_card_query(card_id: int, user: User):
    if check_card(card_id=card_id) == True:
        if check_card_own(card_id=card_id, user=user) == True:
            try:
                session = session_create
                session.execute(delete(Cards).where(Cards.id == card_id))
                session.execute(
                    delete(CardsAccess).where(CardsAccess.card_id == card_id)
                )
                session.commit()
                logger.success("Карта удалена успешно")
                result = {
                    "result": True,
                    "message": "Карта удалена",
                    "category": "success",
                    "cod": 201,
                }
            except Exception as err:
                logger.error(f"Не удалось удалить карту из базы Ошибка {err}")
                result = {
                    "result": False,
                    "message": "Ошибка сервера не удалось удалить карту",
                    "category": "error",
                    "cod": 500,
                }
            finally:
                session.close()
        else:
            result = error_access
    else:
        result = error_card_not_found
    return result
