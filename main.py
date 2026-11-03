from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from routers import auth, posts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="SQLAlchemy 2.0 & FastAPI Auth API",
    lifespan=lifespan,
)

# Router to FastAPI
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
