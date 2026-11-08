import pytest
from fastapi import status
from httpx import AsyncClient

from security import create_access_token


@pytest.fixture
async def authenticated_user(client: AsyncClient):
    """Testler için kayıtlı bir kullanıcı ve"
    " yetkilendirilmiş header döndüren fixture."""
    payload = {
        "username": "post_author",
        "email": "author@example.com",
        "password": "password123",
    }
    res = await client.post("/register", json=payload)
    user_data = res.json()
    token = create_access_token(subject=user_data["id"])
    headers = {"Authorization": f"Bearer {token}"}
    return user_data, headers


@pytest.fixture
async def second_user(client: AsyncClient):
    """Ayrı yetki sınırlarını (Forbidden/Ownership)"
    " test etmek için ikincil kullanıcı."""
    payload = {
        "username": "other_user",
        "email": "other@example.com",
        "password": "password123",
    }
    res = await client.post("/register", json=payload)
    user_data = res.json()
    token = create_access_token(subject=user_data["id"])
    headers = {"Authorization": f"Bearer {token}"}
    return user_data, headers


@pytest.mark.asyncio
async def test_create_post_success(client: AsyncClient, authenticated_user):
    user_data, headers = authenticated_user
    post_payload = {"title": "Test Title", "content": "Test content details."}

    response = await client.post("/posts/", json=post_payload, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == post_payload["title"]
    assert data["content"] == post_payload["content"]
    assert data["user_id"] == user_data["id"]
    assert "id" in data


@pytest.mark.asyncio
async def test_update_post_owner_success(client: AsyncClient, authenticated_user):
    _, headers = authenticated_user

    # Post oluştur
    create_res = await client.post(
        "/posts/",
        json={"title": "Old Title", "content": "Old Content"},
        headers=headers,
    )
    post_id = create_res.json()["id"]

    # Güncelle
    update_payload = {"title": "Updated Title", "content": "Updated Content"}
    response = await client.put(
        f"/posts/{post_id}", json=update_payload, headers=headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == update_payload["title"]


@pytest.mark.asyncio
async def test_update_post_forbidden_for_non_owner(
    client: AsyncClient, authenticated_user, second_user
):
    _, owner_headers = authenticated_user
    _, other_headers = second_user

    # 1. Kullanıcı post oluşturur
    create_res = await client.post(
        "/posts/",
        json={"title": "Owner Title", "content": "Owner Content"},
        headers=owner_headers,
    )
    post_id = create_res.json()["id"]

    # 2. Kullanıcı başkasının postunu güncellemeye çalışır
    update_payload = {"title": "Hacked Title", "content": "Hacked Content"}
    response = await client.put(
        f"/posts/{post_id}", json=update_payload, headers=other_headers
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_post_owner_success(client: AsyncClient, authenticated_user):
    _, headers = authenticated_user

    create_res = await client.post(
        "/posts/",
        json={"title": "To Delete", "content": "Content"},
        headers=headers,
    )
    post_id = create_res.json()["id"]

    response = await client.delete(f"/posts/{post_id}", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_post_forbidden_for_non_owner(
    client: AsyncClient, authenticated_user, second_user
):
    _, owner_headers = authenticated_user
    _, other_headers = second_user

    create_res = await client.post(
        "/posts/",
        json={"title": "Protected Post", "content": "Content"},
        headers=owner_headers,
    )
    post_id = create_res.json()["id"]

    response = await client.delete(f"/posts/{post_id}", headers=other_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_create_post_for_user_endpoint(client: AsyncClient):
    # Kullanıcı oluştur
    reg_res = await client.post(
        "/register",
        json={
            "username": "target_author",
            "email": "target_author@example.com",
            "password": "password123",
        },
    )
    user_id = reg_res.json()["id"]

    post_payload = {
        "title": "Admin Assigned Post",
        "content": "Assigned Content",
    }
    response = await client.post(f"/posts/user/{user_id}", json=post_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == user_id
    assert data["title"] == post_payload["title"]
