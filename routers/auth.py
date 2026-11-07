# routers/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

import schemas
from dependencies import DbSession, RateLimiter
from repositories.user_repository import UserRepository
from services.auth_service import AuthService

# APIRouter örneği oluşturuyoruz
router = APIRouter(
    prefix="",  # İstenirse prefix="/auth" yapılabilir, şimdilik URL'leri korumak için boş bırakıyoruz
    tags=["Auth"],  # Swagger dokümantasyonunda bu grupta görünecek
)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def register_endpoint(
    user_in: schemas.UserCreate,
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.register_user(user_in=user_in)


@router.post(
    "/login",
    response_model=schemas.Token,
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.authenticate_user(
        username_email=form_data.username, password=form_data.password
    )


@router.post(
    "/refresh",
    response_model=schemas.Token,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def refresh_token_endpoint(
    body: schemas.TokenRefreshRequest,
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.refresh_tokens(refresh_token=body.refresh_token)
