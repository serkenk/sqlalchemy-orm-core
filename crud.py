# crud.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas


async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    return new_user


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[models.User]:
    stmt = (
        select(models.User)
        .options(selectinload(models.User.posts))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    stmt = (
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.posts))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user_post(
    db: AsyncSession, post_in: schemas.PostCreate, user_id: int
) -> models.Post:
    new_post = models.Post(
        title=post_in.title,
        content=post_in.content,
        user_id=user_id,
    )
    db.add(new_post)
    await db.flush()
    await db.refresh(new_post)
    return new_post
