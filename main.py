from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
from database import engine, get_db
from repositories.post_repository import PostRepository
from repositories.user_repository import UserRepository
from security import decode_access_token, oauth2_scheme
from services.auth_service import AuthService
from services.post_service import PostService
from services.user_service import UserService

DbSession = Annotated[AsyncSession, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="SQLAlchemy 2.0 & FastAPI Auth API",
    lifespan=lifespan,
)


# --- AUTH ENDPOINTS ---
@app.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_endpoint(
    user_in: schemas.UserCreate,
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.register_user(user_in=user_in)


@app.post("/login", response_model=schemas.Token)
async def login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.authenticate_user(
        username_email=form_data.username, password=form_data.password
    )


@app.post("/refresh", response_model=schemas.Token)
async def refresh_token_endpoint(
    body: schemas.TokenRefreshRequest,
    db: DbSession,
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    return await auth_service.refresh_tokens(refresh_token=body.refresh_token)


# --- DEPENDENCY: AUTHENTICATED USER ---
async def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    """Validates the JWT access token and retrieves the current authenticated user."""
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


# --- PROTECTED POST ENDPOINTS ---
@app.post(
    "/posts/",
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


@app.get("/me", response_model=schemas.UserResponse)
async def read_users_me_endpoint(
    current_user: CurrentUser,
):
    return current_user


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
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


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    post_repo = PostRepository(db)
    post_service = PostService(post_repo)
    await post_service.delete_post(post_id=post_id, current_user=current_user)


# --- USER ENDPOINTS ---
@app.get("/users/", response_model=list[schemas.UserResponse])
async def read_users_endpoint(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return await user_service.get_users(skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user_endpoint(
    user_id: int,
    db: DbSession,
):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    return await user_service.get_user_by_id(user_id=user_id)


@app.post(
    "/users/{user_id}/posts/",
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
