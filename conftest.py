import os
from collections.abc import AsyncGenerator

import pytest_asyncio
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import settings
from database import Base, get_db
from dependencies import get_redis
from main import app

# Konteyner/Local ortamlarına dinamik uyum sağlayan URL tanımları
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.TEST_DATABASE_URL)

REDIS_URL = os.getenv("REDIS_URL", settings.REDIS_URL)

# 1. Test Veritabanı Engine Tanımı (NullPool ile her test sıfır bağlantı kullanır)
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

AsyncTestingSessionFactory = async_sessionmaker(
    bind=engine_test,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# 2. Veritabanı Tablolarını Oluşturma ve Temizleme Fixture'ı
@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 3. İzolasyonlu AsyncSession Fixture'ı
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncTestingSessionFactory() as session:
        yield session


# 4. İzolasyonlu Redis Client Fixture'ı (Her test sonrası DB temizlenir)
@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    """Testler için isolated Redis istemcisi sağlar"
    " ve test sonrası önbelleği temizler."""
    client = aioredis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    yield client
    await client.flushdb()
    await client.aclose()


# 5. Dependency Overrides İçeren HTTPX AsyncClient Fixture'ı
@pytest_asyncio.fixture
async def client(redis_client: aioredis.Redis) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncTestingSessionFactory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def override_get_redis() -> aioredis.Redis:
        return redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
