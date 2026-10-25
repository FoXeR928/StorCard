async def test_get_users_as_admin(client, admin_headers):
    resp = await client.get("/users/", headers=admin_headers)
    assert resp.status_code == 200
    logins = [u["login"] for u in resp.json()]
    assert "admin" in logins


async def test_get_users_as_non_admin(client, user_headers):
    resp = await client.get("/users/", headers=user_headers)
    assert resp.status_code == 403


async def test_register_user(client, admin_headers):
    resp = await client.post(
        "/users/registration",
        json={"login": "newbie", "user_name": "New", "password": "secret"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["result"] is True


async def test_register_duplicate_login(client, admin_headers):
    payload = {"login": "dup", "user_name": "D", "password": "x"}
    r1 = await client.post("/users/registration", json=payload, headers=admin_headers)
    r2 = await client.post("/users/registration", json=payload, headers=admin_headers)
    assert r1.status_code == 201
    assert r2.status_code == 409


async def test_register_by_non_admin_forbidden(client, user_headers):
    resp = await client.post(
        "/users/registration",
        json={"login": "hacker", "user_name": "H", "password": "x"},
        headers=user_headers,
    )
    assert resp.status_code == 403


async def test_change_own_password(client, user_headers, regular_user):
    resp = await client.patch(
        "/users/password",
        json={"login": regular_user["login"], "password": "newpass"},
        headers=user_headers,
    )
    assert resp.status_code == 200

    # Логин со старым паролем — 401
    old = await client.post(
        "/auth/login",
        data={"username": regular_user["login"], "password": regular_user["password"]},
    )
    assert old.status_code == 401

    # Логин с новым — 200
    new = await client.post(
        "/auth/login",
        data={"username": regular_user["login"], "password": "newpass"},
    )
    assert new.status_code == 200


async def test_change_other_password_forbidden(client, user_headers):
    resp = await client.patch(
        "/users/password",
        json={"login": "admin", "password": "hacked"},
        headers=user_headers,
    )
    assert resp.status_code == 403


async def test_admin_can_reset_any_password(client, admin_headers, regular_user):
    resp = await client.patch(
        "/users/password",
        json={"login": regular_user["login"], "password": "resetbyadmin"},
        headers=admin_headers,
    )
    assert resp.status_code == 200


async def test_promote_user_to_admin(client, admin_headers, regular_user):
    resp = await client.patch(
        "/users/role",
        json={"login": regular_user["login"], "is_admin": True},
        headers=admin_headers,
    )
    assert resp.status_code == 200


async def test_cannot_demote_last_admin(client, admin_headers):
    resp = await client.patch(
        "/users/role",
        json={"login": "admin", "is_admin": False},
        headers=admin_headers,
    )
    assert resp.status_code == 403


async def test_update_role_forbidden_for_non_admin(client, user_headers, regular_user):
    resp = await client.patch(
        "/users/role",
        json={"login": regular_user["login"], "is_admin": True},
        headers=user_headers,
    )
    assert resp.status_code == 403


async def test_delete_user(client, admin_headers, regular_user):
    resp = await client.delete(f"/users/{regular_user['login']}", headers=admin_headers)
    assert resp.status_code == 200

    # Повторная попытка логина — 401
    r = await client.post(
        "/auth/login",
        data={"username": regular_user["login"], "password": regular_user["password"]},
    )
    assert r.status_code == 401


async def test_cannot_delete_last_admin(client, admin_headers):
    resp = await client.delete("/users/admin", headers=admin_headers)
    assert resp.status_code == 403


async def test_delete_nonexistent_user(client, admin_headers):
    resp = await client.delete("/users/ghost", headers=admin_headers)
    assert resp.status_code == 404


async def test_delete_user_transfers_cards_to_other_admin(
    client, admin_headers, user_headers, regular_user
):
    from migration_helpers import db_get_card_owner

    # 1. user1 создаёт карту
    r = await client.post(
        "/cards/",
        json={"name": "Наследство", "barcode": "1"},
        headers=user_headers,
    )
    card_id = r.json()["card_id"]

    # 2. Удаляем user1
    resp = await client.delete(f"/users/{regular_user['login']}", headers=admin_headers)
    assert resp.status_code == 200

    # 3. Наследник — admin (самый старый админ), а не кто-то другой
    assert await db_get_card_owner("1") == "admin"

    # 4. Карта жива
    detail = await client.get(f"/cards/{card_id}", headers=admin_headers)
    assert detail.status_code == 200