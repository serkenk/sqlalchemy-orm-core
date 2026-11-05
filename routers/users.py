# routers/users.py
import asyncio

from fastapi import APIRouter

import schemas
from dependencies import CurrentUser, DbSession, RedisSession
from repositories.user_repository import UserRepository
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# 1. Giriş Yapan Kullanıcının Kendi Profil Bilgisi
# URL: GET /users/me
@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me_endpoint(current_user: CurrentUser):
    await asyncio.sleep(2)
    return current_user


# 2. Tüm Kullanıcıları Listeleme (Sayfalamalı / Pagination)
# URL: GET /users/
@router.get("/", response_model=list[schemas.UserResponse])
async def read_users_endpoint(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return await user_service.get_users(skip=skip, limit=limit)


# 3. ID ile Spesifik Bir Kullanıcı Getirme
# URL: GET /users/{user_id}
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user_endpoint(
    user_id: int,
    db: DbSession,
    redis: RedisSession,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo, redis=redis)
    return await user_service.get_user_by_id(user_id=user_id)
