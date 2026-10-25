"""Тесты GET /admin/migration/export."""

import json

from migration_helpers import create_card_for


async def test_export_as_admin(client, admin_headers):
    resp = await client.get("/admin/migration/export", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, dict)
    assert any(u["login"] == "admin" for u in body["users"])


async def test_export_as_non_admin_forbidden(client, user_headers):
    resp = await client.get("/admin/migration/export", headers=user_headers)
    assert resp.status_code == 403


async def test_export_without_token_unauthorized(client):
    resp = await client.get("/admin/migration/export")
    assert resp.status_code == 401


async def test_export_structure(client, admin_headers):
    body = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    assert body["version"] == 1
    assert isinstance(body["users"], list)
    assert isinstance(body["cards"], list)


async def test_export_includes_password_hash(client, admin_headers, regular_user):
    body = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    users = {u["login"]: u for u in body["users"]}

    assert "admin" in users
    assert regular_user["login"] in users

    assert users["admin"]["password_hash"].startswith("$2")
    assert users[regular_user["login"]]["password_hash"].startswith("$2")


async def test_export_does_not_leak_plaintext(client, admin_headers, regular_user):
    body = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    text = json.dumps(body)
    assert "adminpass" not in text
    assert "userpass" not in text


async def test_export_includes_disabled_flag(client, admin_headers):
    body = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    admin = next(u for u in body["users"] if u["login"] == "admin")
    assert "disabled" in admin
    assert admin["disabled"] is False


async def test_export_includes_cards_with_owner_login(
    client, admin_headers, user_headers, regular_user
):
    await create_card_for(client, user_headers, name="X", barcode="EXP-1")

    body = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    card = next(c for c in body["cards"] if c["barcode"] == "EXP-1")

    assert card["name"] == "X"
    assert card["owner_login"] == regular_user["login"]