# --- SONRASI ---
from typing import Annotated

import jwt
import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

import database
import models
from database import get_db
from repositories.user_repository import UserRepository
from security import decode_access_token, oauth2_scheme

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        token_type: str | None = payload.get("type")
        user_id_str: str | None = payload.get("sub")

        if token_type != "access" or user_id_str is None:
            raise credentials_exception

        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id=user_id)
    if user is None:
        raise credentials_exception
    return user


CurrentUser = Annotated[models.User, Depends(get_current_user)]


# Redis Oturum Bağımlılığı (database.redis_client kullanıyor)
async def get_redis() -> aioredis.Redis:
    if database.redis_client is None:
        raise RuntimeError("Redis client henüz başlatılmadı.")
    return database.redis_client


RedisSession = Annotated[aioredis.Redis, Depends(get_redis)]

# --- RATE LIMITER DEPENDENCY FACTORY ---


class RateLimiter:
    """Redis INCR ve EXPIRE tabanlı Fixed-Window Rate Limiter mekanizması."""

    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds

    async def __call__(
        self,
        request: Request,
        redis: RedisSession,
    ) -> None:
        client_ip = request.client.host if request.client else "127.0.0.1"
        endpoint_path = request.url.path
        cache_key = f"rate_limit:{client_ip}:{endpoint_path}"

        current_requests = await redis.incr(cache_key)

        if current_requests == 1:
            await redis.expire(cache_key, self.seconds)

        if current_requests > self.times:
            ttl = await redis.ttl(cache_key)
            retry_after = ttl if ttl > 0 else self.seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.times} requests per {self.seconds} seconds allowed.",
                headers={"Retry-After": str(retry_after)},
            )
