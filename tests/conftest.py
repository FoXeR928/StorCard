"""
Общие фикстуры для тестов StorCard.

ВАЖНО: переменные окружения устанавливаются до импорта модулей проекта,
иначе db_create.py поднимет рабочую БД.
"""

import os
import tempfile
from pathlib import Path

_TMP_DIR = Path(tempfile.mkdtemp(prefix="storcard_test_"))
os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{_TMP_DIR / 'test.db'}")
os.environ.setdefault("MEDIA_DIR", str(_TMP_DIR / "media"))
os.environ.setdefault("LOGS_DIR", str(_TMP_DIR / "logs"))
os.environ.setdefault("SECRET_KEY_PATH", str(_TMP_DIR / "secret.key"))
os.environ.setdefault("ADMIN_LOGIN", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "adminpass")
os.environ.setdefault("DEBUG", "true")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from db.db_create import Base, engine, ensure_default_admin
from main import app

# ---------- Изоляция БД ----------


@pytest_asyncio.fixture(autouse=True)
async def _reset_db():
    """
    Перед каждым тестом пересоздаём схему и явно создаём админа.
    Event-listener ненадёжен в async-режиме — вызываем helper напрямую.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await ensure_default_admin()
    yield


# ---------- HTTP-клиент ----------


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------- Хелперы ----------


async def login(client: AsyncClient, username: str, password: str) -> str:
    """Возвращает access_token."""
    resp = await client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


# ---------- Фикстуры с админом ----------


@pytest_asyncio.fixture
async def admin_token(client) -> str:
    return await login(client, "admin", "adminpass")


@pytest_asyncio.fixture
async def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


# ---------- Фикстуры с обычным пользователем ----------


@pytest_asyncio.fixture
async def regular_user(client, admin_headers) -> dict:
    """Создаёт regular_user через админский эндпоинт."""
    payload = {"login": "user1", "user_name": "User One", "password": "userpass"}
    resp = await client.post("/users/registration", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return {"login": payload["login"], "password": payload["password"]}


@pytest_asyncio.fixture
async def user_token(client, regular_user) -> str:
    return await login(client, regular_user["login"], regular_user["password"])


@pytest_asyncio.fixture
async def user_headers(user_token) -> dict:
    return {"Authorization": f"Bearer {user_token}"}
