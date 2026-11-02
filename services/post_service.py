# --- YENİ HALİ (services/post_service.py) ---
from fastapi import HTTPException, status

import models
import schemas
from repositories.post_repository import PostRepository


class PostService:
    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    async def create_post(
        self, post_in: schemas.PostCreate, user_id: int
    ) -> models.Post:
        return await self.post_repo.create(post_in=post_in, user_id=user_id)

    async def update_post(
        self, post_id: int, post_in: schemas.PostCreate, current_user: models.User
    ) -> models.Post:
        db_post = await self.post_repo.get_by_id(post_id)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )
        if db_post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this post.",
            )
        return await self.post_repo.update(db_post=db_post, post_in=post_in)

    async def delete_post(self, post_id: int, current_user: models.User) -> None:
        db_post = await self.post_repo.get_by_id(post_id)
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found.",
            )
        if db_post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this post.",
            )
        await self.post_repo.delete(db_post=db_post)
