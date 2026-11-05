# --- SONRASI ---
import json

import redis.asyncio as aioredis
from fastapi import HTTPException, status

import models
import schemas
from repositories.user_repository import UserRepository

USER_CACHE_TTL = 300  # 5 dakika TTL


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        redis: aioredis.Redis | None = None,
    ):
        self.user_repo = user_repo
        self.redis = redis

    async def get_user_by_id(self, user_id: int) -> schemas.UserResponse:
        cache_key = f"user:{user_id}"

        # 1. ÖNBELLEK KONTROLÜ (Cache Read)
        if self.redis:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                user_dict = json.loads(cached_data)
                return schemas.UserResponse.model_validate(user_dict)

        # 2. VERİTABANI SORGU SÜRECİ (Cache MISS)
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı.",
            )

        user_response = schemas.UserResponse.model_validate(user)

        # 3. ÖNBELLEĞE YAZMA (Cache Write + TTL)
        if self.redis:
            await self.redis.set(
                cache_key,
                user_response.model_dump_json(),
                ex=USER_CACHE_TTL,
            )

        return user_response

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        """Tüm kullanıcıları sayfalamalı (pagination) olarak veritabanından getirir."""
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def invalidate_user_cache(self, user_id: int) -> None:
        """Kullanıcı bilgisi güncellendiğinde veya silindiğinde önbelleği temizler."""
        if self.redis:
            await self.redis.delete(f"user:{user_id}")
