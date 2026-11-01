from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas
from security import get_password_hash


async def create_user(db: AsyncSession, user_in: schemas.UserCreate) -> models.User:
    hashed_pwd = get_password_hash(user_in.password)
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pwd,
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    stmt = (
        select(models.User)
        .where(models.User.id == new_user.id)
        .options(selectinload(models.User.posts))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


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


async def get_post_by_id(db: AsyncSession, post_id: int) -> models.Post | None:
    stmt = select(models.Post).where(models.Post.id == post_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_post(
    db: AsyncSession, db_post: models.Post, post_in: schemas.PostCreate
) -> models.Post:
    db_post.title = post_in.title
    db_post.content = post_in.content
    await db.flush()
    await db.refresh(db_post)
    return db_post


async def delete_post(db: AsyncSession, db_post: models.Post) -> None:
    await db.delete(db_post)
    await db.flush()


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
