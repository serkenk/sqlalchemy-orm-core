# dependencies.py
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from repositories.user_repository import UserRepository
from security import decode_access_token, oauth2_scheme

# 1. Veritabanı Oturum Bağımlılığı (Type Alias)
DbSession = Annotated[AsyncSession, Depends(get_db)]


# 2. Mevcut Giriş Yapmış Kullanıcıyı Veritabanından Getiren Dependency
async def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    """JWT Access Token'ı doğrular ve isteği atan kullanıcıyı DB'den çekip döndürür."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        token_type: str | None = payload.get("type")
        user_id_str: str | None = payload.get("sub")

        # Token tipi 'access' değilse veya sub claim'i yoksa reddet
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


# 3. Endpoint Handler'larda Kullanmak İçin Kısayol Tip Tanımı (Type Alias)
CurrentUser = Annotated[models.User, Depends(get_current_user)]
