from contextlib import asynccontextmanager
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import models
import schemas
from database import Base, engine, get_db
from security import (
    create_access_token,
    decode_access_token,
    oauth2_scheme,
    verify_password,
)

DbSession = Annotated[AsyncSession, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="SQLAlchemy 2.0 & FastAPI Auth API",
    lifespan=lifespan,
)


@app.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_endpoint(
    user_in: schemas.UserCreate,
    db: DbSession,
):
    existing_user = await crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )
    return await crud.create_user(db=db, user_in=user_in)


@app.post("/login", response_model=schemas.Token)
async def login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    # Swagger UI username alanına email gönderir
    user = await crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return schemas.Token(access_token=access_token)


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
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception

    user = await crud.get_user_by_id(db, user_id=user_id)
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
    """Creates a new post for the currently authenticated user."""
    return await crud.create_user_post(db=db, post_in=post_in, user_id=current_user.id)


@app.get("/me", response_model=schemas.UserResponse)
async def read_users_me_endpoint(
    current_user: CurrentUser,
):
    """Retrieves the profile information and posts of the currently authenticated user."""
    return current_user


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post_endpoint(
    post_id: int,
    post_in: schemas.PostCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    """Updates a post if it belongs to the currently authenticated user."""
    db_post = await crud.get_post_by_id(db, post_id=post_id)
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
    return await crud.update_post(db=db, db_post=db_post, post_in=post_in)


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    """Deletes a post if it belongs to the currently authenticated user."""
    db_post = await crud.get_post_by_id(db, post_id=post_id)
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
    await crud.delete_post(db=db, db_post=db_post)


@app.get("/users/", response_model=list[schemas.UserResponse])
async def read_users_endpoint(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
):
    return await crud.get_users(db=db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user_endpoint(
    user_id: int,
    db: DbSession,
):
    db_user = await crud.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı.",
        )
    return db_user


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
    db_user = await crud.get_user_by_id(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı.",
        )
    return await crud.create_user_post(db=db, post_in=post_in, user_id=user_id)
