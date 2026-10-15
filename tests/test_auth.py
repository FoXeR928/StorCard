async def test_login_success(client):
    resp = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert "refresh_token" in body  # ← ДОБАВЬ
    assert body["user"]["login"] == "admin"
    assert body["user"]["is_admin"] is True


async def test_refresh_token_returns_new_access(client):
    """POST /auth/refresh обменивает refresh на новый access."""
    login = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass"},
    )
    refresh = login.json()["refresh_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


async def test_refresh_with_garbage_token_401(client):
    resp = await client.post("/auth/refresh", json={"refresh_token": "garbage"})
    assert resp.status_code == 401


async def test_refresh_with_access_token_rejected(client):
    """Access-токен нельзя использовать как refresh."""
    login = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass"},
    )
    access = login.json()["access_token"]

    resp = await client.post("/auth/refresh", json={"refresh_token": access})
    assert resp.status_code == 401


async def test_login_wrong_password(client):
    resp = await client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert resp.status_code == 401


async def test_login_nonexistent_user(client):
    resp = await client.post(
        "/auth/login",
        data={"username": "ghost", "password": "x"},
    )
    assert resp.status_code == 401


async def test_logout(client, admin_headers):
    resp = await client.post("/auth/logout", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["result"] is True


async def test_protected_route_without_token(client):
    resp = await client.get("/cards/")
    assert resp.status_code == 401


async def test_protected_route_with_invalid_token(client):
    resp = await client.get(
        "/cards/",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    assert resp.status_code == 401


async def test_status_endpoint(client):
    resp = await client.get("/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "OK"
