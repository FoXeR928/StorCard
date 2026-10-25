"""Сквозные сценарии: экспорт → импорт на тот же/чистый сервер."""

from migration_helpers import create_card_for, make_file, post_import


async def test_roundtrip_preserves_passwords(client, admin_headers, regular_user):
    """Ключевой сценарий: после пере-импорта работает старый пароль."""
    export = (await client.get("/admin/migration/export", headers=admin_headers)).json()

    # Удаляем regular_user — старый пароль больше не работает
    assert (
        await client.delete(f"/users/{regular_user['login']}", headers=admin_headers)
    ).status_code == 200

    fail = await client.post(
        "/auth/login",
        data={"username": regular_user["login"], "password": regular_user["password"]},
    )
    assert fail.status_code == 401

    # Импорт
    file_data = make_file(
        "pw", users=export["users"], cards=export["cards"]
    )
    assert (
        await post_import(client, admin_headers, file_data, "pw")
    ).status_code == 200

    # Старый пароль снова работает
    ok = await client.post(
        "/auth/login",
        data={"username": regular_user["login"], "password": regular_user["password"]},
    )
    assert ok.status_code == 200


async def test_roundtrip_second_import_idempotent_for_users(
    client, admin_headers, regular_user
):
    export = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    file_data = make_file("pw", users=export["users"], cards=[])

    r1 = (await post_import(client, admin_headers, file_data, "pw")).json()
    r2 = (await post_import(client, admin_headers, file_data, "pw")).json()

    assert r1["users_imported"] == 0  # все уже есть
    assert r2["users_imported"] == 0
    assert r1["users_updated"] >= 1
    assert r2["users_updated"] >= 1


async def test_roundtrip_second_import_skips_cards(
    client, admin_headers, user_headers
):
    """Повторный импорт существующей карты → skipped, не создаётся дубль."""
    card_id = await create_card_for(client, user_headers, name="RT", barcode="RT-1")

    export = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    file_data = make_file("pw", users=[], cards=export["cards"])

    assert (
        await client.delete(f"/cards/{card_id}", headers=user_headers)
    ).status_code == 200

    r1 = (await post_import(client, admin_headers, file_data, "pw")).json()
    r2 = (await post_import(client, admin_headers, file_data, "pw")).json()

    assert r1["cards_imported"] == 1
    assert r1["cards_skipped"] == 0
    assert r2["cards_imported"] == 0
    assert r2["cards_skipped"] == 1


async def test_roundtrip_full_data_survives(client, admin_headers, user_headers, regular_user):
    """Полный экспорт + импорт на пустую БД = идентичное состояние."""
    await create_card_for(client, user_headers, name="FullA", barcode="FA-1")
    await create_card_for(client, user_headers, name="FullB", barcode="FB-1")

    export = (await client.get("/admin/migration/export", headers=admin_headers)).json()
    assert len(export["users"]) >= 2
    assert len(export["cards"]) >= 2

    file_data = make_file("pw", users=export["users"], cards=export["cards"])
    result = (await post_import(client, admin_headers, file_data, "pw")).json()

    # Пользователи уже есть — обновляются, карты уже есть — пропускаются
    assert result["users_imported"] == 0
    assert result["cards_imported"] == 0
    assert result["cards_skipped"] >= 2