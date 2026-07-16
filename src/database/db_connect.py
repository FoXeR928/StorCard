from os import getenv
from pathlib import Path
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.core_config import DB_DRIVER, DB_NAME

if DB_DRIVER == "sqlite":
    Path("./data/db").mkdir(exist_ok=True, parents=True)
    url = f"sqlite+aiosqlite:///./data/db/{DB_NAME}.db"
else:
    driver = "mysql+aiomysql" if DB_DRIVER == "mysql" else "postgresql+asyncpg"
    url = URL.create(
        drivername=driver,
        username=getenv("SQL_USER"),
        password=getenv("SQL_PASSWORD"),
        host=getenv("SQL_HOST"),
        port=getenv("SQL_PORT"),
        database=DB_NAME,
    )

engine = create_async_engine(url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
