import pytest
from fastapi import status
from httpx import AsyncClient

from security import create_access_token
from services.user_service import UserService


# 1. Giriş Yapmış Kullanıcının Profilini Başarıyla Getirme Senaryosu
@pytest.mark.asyncio
async def test_read_users_me_success(client: AsyncClient):
    # Kullanıcı kaydı oluştur
    register_payload = {
        "username": "me_user",
        "email": "me@example.com",
        "password": "password123",
    }
    reg_res = await client.post("/register", json=register_payload)
    user_id = reg_res.json()["id"]

    # Access token üret ve Auth header ayarla
    token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    # /users/me endpoint'ine istek at
    response = await client.get("/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == register_payload["username"]
    assert data["email"] == register_payload["email"]


# 2. Yetkisiz (Token Olmadan) Profil İsteme Senaryosu
@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: AsyncClient):
    response = await client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# 3. Sayfalamalı (Pagination) Kullanıcı Listeleme Senaryosu
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


# 4. ID ile Spesifik Kullanıcı Getirme Senaryosu
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


# 5. Olmayan Kullanıcı ID'si İle İstek Atma Senaryosu
@pytest.mark.asyncio
async def test_read_user_by_id_not_found(client: AsyncClient):
    response = await client.get("/users/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 6. Redis Önbellekleme (Cache MISS ve Cache HIT) Doğrulama Senaryosu
@pytest.mark.asyncio
async def test_read_user_by_id_caching(client: AsyncClient, redis_client):
    # Kullanıcı kaydı oluştur
    reg_res = await client.post(
        "/register",
        json={
            "username": "cache_user",
            "email": "cache@example.com",
            "password": "password123",
        },
    )
    user_id = reg_res.json()["id"]

    # Önbellekte anahtarın henüz olmadığını doğrula
    cache_key = f"user:{user_id}"
    assert await redis_client.get(cache_key) is None

    # GET /users/{user_id} çağrısı yap (Cache MISS -> DB -> Write to Redis)
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK

    # Redis'e verinin yazıldığını doğrula (Cache HIT hazırlığı)
    cached_data = await redis_client.get(cache_key)
    assert cached_data is not None
    assert "cache_user" in cached_data


# 7. Önbellek Temizleme (Cache Invalidation) Senaryosu
@pytest.mark.asyncio
async def test_invalidate_user_cache(client: AsyncClient, redis_client):
    """UserService.invalidate_user_cache metodunun Redis'teki anahtarı sildiğini doğrular."""

    # 1. Kullanıcı kaydı oluştur
    reg_res = await client.post(
        "/register",
        json={
            "username": "invalidation_user",
            "email": "invalid@example.com",
            "password": "password123",
        },
    )
    user_id = reg_res.json()["id"]

    # 2. Endpoint'e istek atarak veriyi önbelleğe yazdır
    await client.get(f"/users/{user_id}")
    cache_key = f"user:{user_id}"
    assert await redis_client.get(cache_key) is not None

    # 3. Cache Invalidation çalıştır ve anahtarın silindiğini doğrula
    user_service = UserService(user_repo=None, redis=redis_client)
    await user_service.invalidate_user_cache(user_id=user_id)
    assert await redis_client.get(cache_key) is None
