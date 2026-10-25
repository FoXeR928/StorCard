"""Тесты POST /admin/migration/import."""

import hashlib
import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from migration_helpers import (
    db_get_card,
    db_get_card_owner,
    db_get_user,
    make_file,
    post_import,
)


# --------------------------------------------------------------------------- #
# Авторизация
# --------------------------------------------------------------------------- #


async def test_import_as_non_admin_forbidden(client, user_headers):
    data = make_file("pw", users=[], cards=[])
    resp = await post_import(client, user_headers, data, "pw")
    assert resp.status_code == 403


async def test_import_without_token_unauthorized(client):
    resp = await client.post(
        "/admin/migration/import",
        files={"file": ("d.storcard", b"\x00" * 64, "application/octet-stream")},
        data={"password": "pw"},
    )
    assert resp.status_code == 401


# --------------------------------------------------------------------------- #
# Валидация файла
# --------------------------------------------------------------------------- #


async def test_import_empty_file_400(client, admin_headers):
    resp = await client.post(
        "/admin/migration/import",
        files={"file": ("d.storcard", b"", "application/octet-stream")},
        data={"password": "pw"},
        headers=admin_headers,
    )
    assert resp.status_code == 400


async def test_import_too_short_file_400(client, admin_headers):
    resp = await post_import(client, admin_headers, b"\x00" * 10, "pw")
    assert resp.status_code == 400


async def test_import_unaligned_file_400(client, admin_headers):
    # 36 байт = IV(16) + 20 — размер шифротекста не кратен 16
    resp = await post_import(client, admin_headers, b"\x00" * 36, "pw")
    assert resp.status_code == 400


async def test_import_wrong_password_400(client, admin_headers):
    data = make_file("correct", users=[])
    resp = await post_import(client, admin_headers, data, "wrong")
    assert resp.status_code == 400


async def test_import_wrong_version_400(client, admin_headers):
    data = make_file("pw", users=[], cards=[], version=99)
    resp = await post_import(client, admin_headers, data, "pw")
    assert resp.status_code == 400


async def test_import_missing_version_400(client, admin_headers):
    data = make_file("pw", users=[], cards=[], version=None)
    resp = await post_import(client, admin_headers, data, "pw")
    assert resp.status_code == 400


async def test_import_corrupted_plaintext_400(client, admin_headers):
    """Валидное AES, но plaintext не JSON → json.loads падает → 400."""
    key = hashlib.sha256(b"pw").digest()
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    padded = padder.update(b"not-a-json") + padder.finalize()
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    data = iv + enc.update(padded) + enc.finalize()

    resp = await post_import(client, admin_headers, data, "pw")
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# Пользователи
# --------------------------------------------------------------------------- #


async def test_import_creates_new_user(client, admin_headers):
    data = make_file(
        "pw",
        users=[
            {"login": "imp1", "user_name": "I1", "is_admin": False}
        ],
        cards=[],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()

    assert body["result"] is True
    assert body["users_imported"] == 1
    assert body["users_updated"] == 0

    u = await db_get_user("imp1")
    assert u is not None
    assert u.user_name == "I1"
    assert u.is_admin is False


async def test_import_user_without_hash_gets_default_password(client, admin_headers):
    data = make_file(
        "pw", users=[{"login": "nohash", "user_name": "N", "is_admin": False}], cards=[]
    )
    resp = await post_import(client, admin_headers, data, "pw")
    assert resp.status_code == 200
    assert resp.json()["users_imported"] == 1

    ok = await client.post(
        "/auth/login",
        data={"username": "nohash", "password": "storcard_import"},
    )
    assert ok.status_code == 200


async def test_import_updates_existing_user_role(client, admin_headers, regular_user):
    data = make_file(
        "pw",
        users=[{"login": regular_user["login"], "is_admin": True}],
        cards=[],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()

    assert body["users_imported"] == 0
    assert body["users_updated"] == 1

    u = await db_get_user(regular_user["login"])
    assert u.is_admin is True


async def test_import_skips_user_without_login(client, admin_headers):
    data = make_file(
        "pw",
        users=[
            {"user_name": "NoLogin", "is_admin": False},  # без login
            {"login": "ok_user", "user_name": "OK", "is_admin": False},
        ],
        cards=[],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["users_imported"] == 1
    assert await db_get_user("ok_user") is not None


async def test_import_preserves_disabled_flag(client, admin_headers):
    data = make_file(
        "pw",
        users=[{"login": "dis", "user_name": "D", "is_admin": False, "disabled": True}],
        cards=[],
    )
    await post_import(client, admin_headers, data, "pw")

    u = await db_get_user("dis")
    assert u.disabled is True

    login = await client.post(
        "/auth/login",
        data={"username": "dis", "password": "storcard_import"},
    )
    assert login.status_code == 401


# --------------------------------------------------------------------------- #
# Карты
# --------------------------------------------------------------------------- #


async def test_import_creates_card_with_explicit_owner(
    client, admin_headers, regular_user
):
    data = make_file(
        "pw",
        users=[],
        cards=[
            {
                "name": "Owned",
                "barcode": "OWNED-1",
                "owner_login": regular_user["login"],
            }
        ],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["cards_imported"] == 1
    assert body["cards_skipped"] == 0

    owner = await db_get_card_owner("OWNED-1")
    assert owner == regular_user["login"]


async def test_import_card_with_unknown_owner_falls_back_to_admin(
    client, admin_headers
):
    data = make_file(
        "pw",
        users=[],
        cards=[{"name": "Orphan", "barcode": "ORPHAN-1", "owner_login": "ghost"}],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["cards_imported"] == 1

    assert await db_get_card_owner("ORPHAN-1") == "admin"


async def test_import_card_without_owner_login_falls_back_to_admin(
    client, admin_headers
):
    data = make_file(
        "pw",
        users=[],
        cards=[{"name": "NoOwner", "barcode": "NOOWNER-1"}],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["cards_imported"] == 1
    assert await db_get_card_owner("NOOWNER-1") == "admin"


async def test_import_card_without_barcode_is_skipped(client, admin_headers):
    data = make_file(
        "pw",
        users=[],
        cards=[{"name": "NoBarcode", "owner_login": "admin"}],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["cards_imported"] == 0
    # без barcode карта не попадает даже в skipped (continue до логики счёта)
    assert body["cards_skipped"] == 0


async def test_import_skips_duplicate_barcode(client, admin_headers):
    data = make_file(
        "pw",
        users=[],
        cards=[{"name": "Dup", "barcode": "DUP-1", "owner_login": "admin"}],
    )
    r1 = (await post_import(client, admin_headers, data, "pw")).json()
    r2 = (await post_import(client, admin_headers, data, "pw")).json()

    assert r1["cards_imported"] == 1
    assert r2["cards_imported"] == 0
    assert r2["cards_skipped"] == 1


async def test_import_card_visible_to_owner_after_import(
    client, admin_headers, regular_user, user_headers
):
    data = make_file(
        "pw",
        users=[],
        cards=[
            {
                "name": "Visible",
                "barcode": "VIS-1",
                "owner_login": regular_user["login"],
            }
        ],
    )
    await post_import(client, admin_headers, data, "pw")

    lst = await client.get("/cards/", headers=user_headers)
    assert any(c["barcode"] == "VIS-1" for c in lst.json())


# --------------------------------------------------------------------------- #
# Крайние случаи
# --------------------------------------------------------------------------- #


async def test_import_empty_payload(client, admin_headers):
    data = make_file("pw", users=[], cards=[])
    body = (await post_import(client, admin_headers, data, "pw")).json()

    assert body["result"] is True
    assert body["users_imported"] == 0
    assert body["users_updated"] == 0
    assert body["cards_imported"] == 0
    assert body["cards_skipped"] == 0


async def test_import_only_cards_no_users(client, admin_headers):
    data = make_file(
        "pw",
        users=[],
        cards=[{"name": "OnlyCard", "barcode": "ONLY-1", "owner_login": "ghost"}],
    )
    body = (await post_import(client, admin_headers, data, "pw")).json()
    assert body["cards_imported"] == 1
    assert await db_get_card_owner("ONLY-1") == "admin"