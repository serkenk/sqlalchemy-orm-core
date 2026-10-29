import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import AsyncSessionFactory, Base, engine
from models import Post, User


async def init_db() -> None:
    # Models içindeki Base'den türeyen tabloları veritabanında otomatik oluşturur
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main() -> None:
    await init_db()

    # 1. İlişkili Veri Ekleme (User + Posts)
    async with AsyncSessionFactory() as session, session.begin():
        new_user = User(
            username="writer_user",
            email="writer@example.com",
            posts=[
                Post(
                    title="SQLAlchemy 2.0 ORM Giriş",
                    content="Async ORM ve ilişki yönetimi.",
                ),
                Post(
                    title="PostgreSQL Entegrasyonu",
                    content="Asyncpg ile ilişkisel veri tabanı kullanımı.",
                ),
            ],
        )
        session.add(new_user)

    # 2. İlişkili Veriyi Sorgulama (selectinload)
    async with AsyncSessionFactory() as session:
        stmt = (
            select(User)
            .where(User.username == "writer_user")
            .options(selectinload(User.posts))
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            print(f"\nKullanıcı: {user.username} (ID: {user.id})")
            for post in user.posts:
                print(f"  - Gönderi ID: {post.id} | Başlık: {post.title}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
