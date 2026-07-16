from loguru import logger
from database.models.model_default import Base
from database.db_connect import engine
from database.repository.repo_users import create_default_users


async def init_db_async():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("Асинхронная база данных инициализирована (таблицы созданы)")
        await create_default_users()
    except Exception as err:
        logger.critical(f"Не удалось инициализировать асинхронную БД: {err}")
        raise err
