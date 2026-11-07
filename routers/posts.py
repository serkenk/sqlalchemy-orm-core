# routers/posts.py
from fastapi import APIRouter, status

import schemas
from dependencies import CurrentUser, DbSession
from repositories.post_repository import PostRepository
from repositories.user_repository import UserRepository
from services.post_service import PostService
from services.user_service import UserService

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


# 1. Yeni Post Oluşturma (Giriş Yapmış Kullanıcı İçin)
# URL: POST /posts/
@router.post(
    "/",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post_endpoint(
    post_in: schemas.PostCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    post_repo = PostRepository(db)
    post_service = PostService(post_repo)
    return await post_service.create_post(post_in=post_in, user_id=current_user.id)


# 2. Post Güncelleme (Sadece Sahibi Güncelleyebilir)
# URL: PUT /posts/{post_id}
@router.put("/{post_id}", response_model=schemas.PostResponse)
async def update_post_endpoint(
    post_id: int,
    post_in: schemas.PostCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    post_repo = PostRepository(db)
    post_service = PostService(post_repo)
    return await post_service.update_post(
        post_id=post_id, post_in=post_in, current_user=current_user
    )


# 3. Post Silme (Sadece Sahibi Silebilir)
# URL: DELETE /posts/{post_id}
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    post_repo = PostRepository(db)
    post_service = PostService(post_repo)
    await post_service.delete_post(post_id=post_id, current_user=current_user)


# 4. Belirli Bir Kullanıcı Adına Post Oluşturma
# URL: POST /posts/user/{user_id}
@router.post(
    "/user/{user_id}",
    response_model=schemas.PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post_for_user_endpoint(
    user_id: int,
    post_in: schemas.PostCreate,
    db: DbSession,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    await user_service.get_user_by_id(user_id=user_id)

    post_repo = PostRepository(db)
    post_service = PostService(post_repo)
    return await post_service.create_post(post_in=post_in, user_id=user_id)
