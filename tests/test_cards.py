async def create_card(
    client,
    headers,
    name: str = "Лента",
    about: str = "Продукты",
    barcode: str = "1234567890",
) -> str:
    resp = await client.post(
        "/cards/",
        json={"name": name, "about": about, "barcode": barcode},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["card_id"]


async def make_user(client, admin_headers, login: str, password: str = "p") -> dict:
    resp = await client.post(
        "/users/registration",
        json={"login": login, "user_name": login, "password": password},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    r = await client.post("/auth/login", data={"username": login, "password": password})
    assert r.status_code == 200
    return {
        "login": login,
        "password": password,
        "headers": {"Authorization": f"Bearer {r.json()['access_token']}"},
    }


# ---------- CRUD ----------


async def test_create_card(client, user_headers):
    card_id = await create_card(client, user_headers)
    assert isinstance(card_id, str)
    assert len(card_id) > 0


async def test_get_my_cards(client, user_headers):
    await create_card(client, user_headers, name="A")
    await create_card(client, user_headers, name="B")
    resp = await client.get("/cards/", headers=user_headers)
    assert resp.status_code == 200
    names = sorted(c["name"] for c in resp.json())
    assert names == ["A", "B"]


async def test_get_all_cards_as_admin(client, admin_headers, user_headers):
    await create_card(client, user_headers, name="X")
    resp = await client.get("/cards/all", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_get_all_cards_as_non_admin_forbidden(client, user_headers):
    resp = await client.get("/cards/all", headers=user_headers)
    assert resp.status_code == 403


async def test_get_card_detail(client, user_headers):
    card_id = await create_card(client, user_headers, name="Лента")
    resp = await client.get(f"/cards/{card_id}", headers=user_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Лента"
    assert body["my_access_level"] == "owner"


async def test_get_nonexistent_card(client, user_headers):
    resp = await client.get(
        "/cards/00000000-0000-0000-0000-000000000000", headers=user_headers
    )
    assert resp.status_code in (403, 404)


async def test_update_card(client, user_headers):
    card_id = await create_card(client, user_headers)
    resp = await client.patch(
        f"/cards/{card_id}",
        json={"name": "Перекрёсток"},
        headers=user_headers,
    )
    assert resp.status_code == 200

    detail = await client.get(f"/cards/{card_id}", headers=user_headers)
    assert detail.json()["name"] == "Перекрёсток"


async def test_update_card_clear_field(client, user_headers):
    """Проверяет, что about можно обнулить через явный null."""
    card_id = await create_card(client, user_headers, about="Продукты")
    resp = await client.patch(
        f"/cards/{card_id}",
        json={"about": None},
        headers=user_headers,
    )
    assert resp.status_code == 200
    detail = await client.get(f"/cards/{card_id}", headers=user_headers)
    assert detail.json()["about"] is None


async def test_update_card_empty_payload(client, user_headers):
    card_id = await create_card(client, user_headers)
    resp = await client.patch(f"/cards/{card_id}", json={}, headers=user_headers)
    assert resp.status_code == 400


async def test_delete_card(client, user_headers):
    card_id = await create_card(client, user_headers)
    resp = await client.delete(f"/cards/{card_id}", headers=user_headers)
    assert resp.status_code == 200

    # После удаления доступа нет
    detail = await client.get(f"/cards/{card_id}", headers=user_headers)
    assert detail.status_code in (403, 404)


# ---------- Шеринг ----------


async def test_share_card_as_viewer(client, admin_headers, user_headers):
    viewer = await make_user(client, admin_headers, "viewer1")
    card_id = await create_card(client, user_headers)
    resp = await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": viewer["login"], "access_level": "viewer"},
        headers=user_headers,
    )
    assert resp.status_code == 201

    # viewer видит карту
    lst = await client.get("/cards/", headers=viewer["headers"])
    assert any(c["id"] == card_id for c in lst.json())


async def test_share_card_invalid_level(client, admin_headers, user_headers):
    await make_user(client, admin_headers, "viewer2")
    card_id = await create_card(client, user_headers)
    resp = await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": "viewer2", "access_level": "owner"},
        headers=user_headers,
    )
    assert resp.status_code == 400


async def test_share_card_duplicate(client, admin_headers, user_headers):
    await make_user(client, admin_headers, "viewer3")
    card_id = await create_card(client, user_headers)
    payload = {"target_login": "viewer3", "access_level": "viewer"}
    r1 = await client.post(
        f"/cards/{card_id}/share", json=payload, headers=user_headers
    )
    r2 = await client.post(
        f"/cards/{card_id}/share", json=payload, headers=user_headers
    )
    assert r1.status_code == 201
    assert r2.status_code == 400


async def test_share_card_to_nonexistent_user(client, user_headers):
    card_id = await create_card(client, user_headers)
    resp = await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": "ghost", "access_level": "viewer"},
        headers=user_headers,
    )
    assert resp.status_code == 404


# ---------- Права ----------


async def test_viewer_cannot_edit(client, admin_headers, user_headers):
    viewer = await make_user(client, admin_headers, "viewer4")
    card_id = await create_card(client, user_headers)
    await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": viewer["login"], "access_level": "viewer"},
        headers=user_headers,
    )
    resp = await client.patch(
        f"/cards/{card_id}",
        json={"name": "Hacked"},
        headers=viewer["headers"],
    )
    assert resp.status_code == 403


async def test_editor_can_edit(client, admin_headers, user_headers):
    editor = await make_user(client, admin_headers, "editor1")
    card_id = await create_card(client, user_headers)
    await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": editor["login"], "access_level": "editor"},
        headers=user_headers,
    )
    resp = await client.patch(
        f"/cards/{card_id}",
        json={"name": "Changed by editor"},
        headers=editor["headers"],
    )
    assert resp.status_code == 200


async def test_viewer_cannot_delete(client, admin_headers, user_headers):
    viewer = await make_user(client, admin_headers, "viewer5")
    card_id = await create_card(client, user_headers)
    await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": viewer["login"], "access_level": "viewer"},
        headers=user_headers,
    )
    resp = await client.delete(f"/cards/{card_id}", headers=viewer["headers"])
    assert resp.status_code == 403


async def test_editor_cannot_delete(client, admin_headers, user_headers):
    editor = await make_user(client, admin_headers, "editor2")
    card_id = await create_card(client, user_headers)
    await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": editor["login"], "access_level": "editor"},
        headers=user_headers,
    )
    resp = await client.delete(f"/cards/{card_id}", headers=editor["headers"])
    assert resp.status_code == 403


async def test_admin_can_access_any_card(client, admin_headers, user_headers):
    card_id = await create_card(client, user_headers)
    resp = await client.get(f"/cards/{card_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["my_access_level"] == "admin"


# ---------- Передача владения ----------


async def test_change_owner(client, admin_headers, user_headers):
    new_owner = await make_user(client, admin_headers, "newowner")
    card_id = await create_card(client, user_headers)

    resp = await client.put(
        f"/cards/{card_id}/owner",
        json={"target_login": new_owner["login"]},
        headers=user_headers,
    )
    assert resp.status_code == 200

    # Старый владелец стал editor
    d1 = await client.get(f"/cards/{card_id}", headers=user_headers)
    assert d1.json()["my_access_level"] == "editor"

    # Новый владелец — owner
    d2 = await client.get(f"/cards/{card_id}", headers=new_owner["headers"])
    assert d2.json()["my_access_level"] == "owner"


async def test_change_owner_to_self_forbidden(client, user_headers, regular_user):
    card_id = await create_card(client, user_headers)
    resp = await client.put(
        f"/cards/{card_id}/owner",
        json={"target_login": regular_user["login"]},
        headers=user_headers,
    )
    assert resp.status_code == 400


async def test_change_owner_by_editor_forbidden(client, admin_headers, user_headers):
    editor = await make_user(client, admin_headers, "editor3")
    target = await make_user(client, admin_headers, "target1")
    card_id = await create_card(client, user_headers)
    await client.post(
        f"/cards/{card_id}/share",
        json={"target_login": editor["login"], "access_level": "editor"},
        headers=user_headers,
    )
    resp = await client.put(
        f"/cards/{card_id}/owner",
        json={"target_login": target["login"]},
        headers=editor["headers"],
    )
    assert resp.status_code == 403
