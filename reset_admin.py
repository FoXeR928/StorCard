import asyncio
import os
import secrets
from loguru import logger
from sqlalchemy import select

from db.db_create import session_create, Users

async def reset_admin():
    admin_login = os.getenv("ADMIN_LOGIN", "admin")
    admin_name = os.getenv("ADMIN_NAME", "Администратор")
    
    # Генерируем случайный пароль (24 байта в base64 = ровно 32 символа)
    new_password = secrets.token_urlsafe(24)

    async with session_create() as session:
        # Ищем пользователя
        user = (await session.scalars(select(Users).where(Users.login == admin_login))).one_or_none()

        if user:
            # Меняем пароль существующему админу
            user.set_password(new_password)
            user.is_admin = True  # На всякий случай восстанавливаем права
            user.disabled = False
            await session.commit()
            action = "Пароль успешно сброшен"
        else:
            # Создаем нового админа, если его нет
            new_admin = Users(
                login=admin_login,
                user_name=admin_name,
                is_admin=True,
                disabled=False,
            )
            new_admin.set_password(new_password)
            session.add(new_admin)
            await session.commit()
            action = "Создан новый администратор"

    # Красивый вывод в консоль
    print("\n" + "=" * 60)
    print(f" 🛠  {action.upper()}!")
    print("=" * 60)
    print(f" Логин:  {admin_login}")
    print(f" Пароль: {new_password}")
    print("=" * 60)
    print("Сохраните этот пароль, он больше не будет показан!\n")

if __name__ == "__main__":
    # Инициализируем логирование, чтобы не было мусора
    logger.remove()
    asyncio.run(reset_admin())