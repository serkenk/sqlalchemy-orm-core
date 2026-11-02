from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas
from security import get_password_hash


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_in: schemas.UserCreate) -> models.User:
        hashed_pwd = get_password_hash(user_in.password)
        new_user = models.User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pwd,
        )
        self.db.add(new_user)
        await self.db.flush()
        await self.db.refresh(new_user)
        
        stmt = (
            select(models.User)
            .where(models.User.id == new_user.id)
            .options(selectinload(models.User.posts))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_by_email(self, email: str) -> models.User | None:
        stmt = select(models.User).where(models.User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> models.User | None:
        stmt = (
            select(models.User)
            .where(models.User.id == user_id)
            .options(selectinload(models.User.posts))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[models.User]:
        stmt = (
            select(models.User)
            .options(selectinload(models.User.posts))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())