from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, post_id: int) -> models.Post | None:
        stmt = select(models.Post).where(models.Post.id == post_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, post_in: schemas.PostCreate, user_id: int) -> models.Post:
        new_post = models.Post(
            title=post_in.title,
            content=post_in.content,
            user_id=user_id,
        )
        self.db.add(new_post)
        await self.db.flush()
        await self.db.refresh(new_post)
        return new_post

    async def update(
        self, db_post: models.Post, post_in: schemas.PostCreate
    ) -> models.Post:
        db_post.title = post_in.title
        db_post.content = post_in.content
        await self.db.flush()
        await self.db.refresh(db_post)
        return db_post

    async def delete(self, db_post: models.Post) -> None:
        await self.db.delete(db_post)
        await self.db.flush()
