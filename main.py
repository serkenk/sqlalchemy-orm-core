# --- SONRASI ---
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI

import database
from config import settings
from database import engine
from routers import auth, posts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Redis bağlantısını database katmanı üzerinden başlatıyoruz
    database.redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    yield
    # Uygulama kapanırken kaynakları temizliyoruz
    await engine.dispose()
    if database.redis_client:
        await database.redis_client.aclose()


app = FastAPI(
    title="SQLAlchemy 2.0 & FastAPI Auth API",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
