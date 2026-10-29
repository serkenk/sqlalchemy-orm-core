import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# .env dosyasındaki değişkenleri yükle
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL ortam değişkeni bulunamadı.")

# 1. Asenkron veritabanı motorunu oluştur
# echo=True parametresi, SQLAlchemy'nin arka planda çalıştırdığı SQL sorgularını konsolda görmeni sağlar.
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Oturum (Session) üretici yapıyı tanımla
# Veritabanı üzerinde işlem yapacağımız zaman bu oturum üreticiyi kullanacağız.
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# 3. Tüm ORM modellerimizin (tablolarımızın) türeyeceği ana taban sınıf
class Base(DeclarativeBase):
    pass