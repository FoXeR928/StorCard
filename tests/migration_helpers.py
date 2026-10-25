"""
Общие хелперы для тестов миграции.

Импорт: `from migration_helpers import ...` — pytest добавляет каталог
с тестами в sys.path (prepend import mode без __init__.py).
"""

import hashlib
import json
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from sqlalchemy import select

from db.db_create import session_create, Users, Cards, CardsAccess
from db.db_migration import MIGRATION_VERSION

# --------------------------------------------------------------------------- #
# Шифрование (зеркало core.crypto_utils.decrypt_storcard_file)
# --------------------------------------------------------------------------- #


def encrypt_storcard(password: str, payload: dict) -> bytes:
    key = hashlib.sha256(password.encode("utf-8")).digest()
    iv = os.urandom(16)
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    padder = padding.PKCS7(128).padder()
    padded = padder.update(raw) + padder.finalize()

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return iv + ciphertext


def make_file(
    password: str,
    *,
    users: list | None = None,
    cards: list | None = None,
    version: int | None = MIGRATION_VERSION,
) -> bytes:
    payload: dict = {}
    if version is not None:
        payload["version"] = version
    if users is not None:
        payload["users"] = users
    if cards is not None:
        payload["cards"] = cards
    return encrypt_storcard(password, payload)


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #


async def post_import(client, headers, file_bytes: bytes, password: str):
    return await client.post(
        "/admin/migration/import",
        files={"file": ("data.storcard", file_bytes, "application/octet-stream")},
        data={"password": password},
        headers=headers,
    )


async def create_card_for(client, headers, name="Test", barcode="bc-1") -> str:
    resp = await client.post(
        "/cards/", json={"name": name, "barcode": barcode}, headers=headers
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["card_id"]


# --------------------------------------------------------------------------- #
# БД
# --------------------------------------------------------------------------- #


async def db_get_user(login: str):
    async with session_create() as session:
        return (
            await session.scalars(select(Users).where(Users.login == login))
        ).one_or_none()


async def db_get_card(barcode: str):
    async with session_create() as session:
        return (
            await session.scalars(select(Cards).where(Cards.barcode == barcode))
        ).one_or_none()


async def db_get_card_owner(barcode: str) -> str:
    """Логин владельца карты по barcode (access_level='owner')."""
    async with session_create() as session:
        card = (
            await session.scalars(select(Cards).where(Cards.barcode == barcode))
        ).one_or_none()
        assert card, f"карта {barcode} не найдена"

        access = (
            await session.scalars(
                select(CardsAccess).where(
                    CardsAccess.card_id == card.id,
                    CardsAccess.access_level == "owner",
                )
            )
        ).one_or_none()
        assert access, f"нет owner-access у карты {barcode}"

        owner = (
            await session.scalars(select(Users).where(Users.id == access.user_id))
        ).one()
        return owner.login