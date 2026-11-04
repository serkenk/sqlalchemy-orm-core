import pytest
from fastapi import status
from httpx import AsyncClient

from security import create_access_token


@pytest.mark.asyncio
async def test_read_users_me_success(client: AsyncClient):
    # 1. Kullanıcı kaydı oluştur
    register_payload = {
        "username": "me_user",
        "email": "me@example.com",
        "password": "password123",
    }
    reg_res = await client.post("/register", json=register_payload)
    user_id = reg_res.json()["id"]

    # 2. Access token üret ve Auth header ayarla
    token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # 3. /users/me endpoint'ine istek at
    response = await client.get("/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == register_payload["username"]
    assert data["email"] == register_payload["email"]


@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: AsyncClient):
    # Yetkisiz (Token olmadan) istek senaryosu
    response = await client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_read_users_pagination(client: AsyncClient):
    # Birden fazla kullanıcı kaydet
    for i in range(3):
        await client.post(
            "/register",
            json={
                "username": f"user_{i}",
                "email": f"user_{i}@example.com",
                "password": "password123",
            },
        )

    # Limit ve skip parametreleri ile sorgula
    response = await client.get("/users/?skip=0&limit=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_read_user_by_id_success(client: AsyncClient):
    reg_res = await client.post(
        "/register",
        json={
            "username": "target_user",
            "email": "target@example.com",
            "password": "password123",
        },
    )
    user_id = reg_res.json()["id"]

    response = await client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_read_user_by_id_not_found(client: AsyncClient):
    response = await client.get("/users/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
