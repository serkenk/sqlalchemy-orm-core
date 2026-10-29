# main.py
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
from database import Base, engine, get_db

DbSession = Annotated[AsyncSession, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başlarken tabloların veritabanında hazır olduğunu doğrular
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Uygulama durdurulduğunda bağlantı havuzunu temizler
    await engine.dispose()


app = FastAPI(
    title="SQLAlchemy 2.0 & FastAPI Entegrasyonu",
    lifespan=lifespan,
)


@app.post(
    "/users/",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_endpoint(
    user_in: schemas.UserCreate,
    db: DbSession,
):
    return await crud.create_user(db=db, user_in=user_in)


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
