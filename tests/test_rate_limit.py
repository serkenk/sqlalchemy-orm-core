import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient, redis_client):
    """/login endpoint'inin 5 istek sınırını uyguladığını doğrular."""
    login_data = {
        "username": "nonexistent_user",
        "password": "some_password",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # İzin verilen 5 isteği gönderiyoruz
    for _ in range(5):
        response = await client.post("/login", data=login_data, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 6. İstekte HTTP 429 Too Many Requests alınmalı
    exceeded_response = await client.post("/login", data=login_data, headers=headers)
    assert exceeded_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Retry-After" in exceeded_response.headers
    assert "Rate limit exceeded" in exceeded_response.json()["detail"]


@pytest.mark.asyncio
async def test_register_rate_limiting(client: AsyncClient, redis_client):
    """/register endpoint'inin rate limit sınırını doğrular."""
    payload = {
        "username": "limiter_user",
        "email": "limit@example.com",
        "password": "password123",
    }

    # İzin verilen 5 isteği gönderiyoruz
    for _ in range(5):
        await client.post("/register", json=payload)

    # 6. İstekte limit aşılmalı
    exceeded_response = await client.post("/register", json=payload)
    assert exceeded_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exceeded_response.headers.get("Retry-After") is not None
