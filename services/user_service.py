from fastapi import HTTPException, status

import models
from repositories.user_repository import UserRepository


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, user_id: int) -> models.User:
        user = await self.user_repo.get_by_id(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı.",
            )
        return user

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        return await self.user_repo.get_all(skip=skip, limit=limit)
