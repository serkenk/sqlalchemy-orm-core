import pytest
from fastapi import status
from httpx import AsyncClient


# 1. Başarılı Kayıt Senaryosu
@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123",
    }
    response = await client.post("/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "password" not in data


# 2. Aynı E-posta İle Tekrar Kayıt Olunama Senaryosu
@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    res1 = await client.post("/register", json=payload)
    assert res1.status_code == status.HTTP_201_CREATED

    duplicate_payload = {
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    response = await client.post("/register", json=duplicate_payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# 3. Başarılı Giriş ve Token Alma Senaryosu
@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    register_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "correctpassword",
    }
    await client.post("/register", json=register_payload)

    login_data = {
        "username": "loginuser",
        "password": "correctpassword",
    }
    response = await client.post(
        "/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


# 4. Hatalı Şifre İle Giriş Denemesi
@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    register_payload = {
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "correctpassword",
    }
    await client.post("/register", json=register_payload)

    login_data = {
        "username": "wrongpassuser",
        "password": "wrongpassword",
    }
    response = await client.post(
        "/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
