import jwt
from fastapi import HTTPException, status

import models
import schemas
from repositories.user_repository import UserRepository
from security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_password,
)


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: schemas.UserCreate) -> models.User:
        existing_user = await self.user_repo.get_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered.",
            )
        return await self.user_repo.create(user_in=user_in)

    async def authenticate_user(
        self, username_email: str, password: str
    ) -> schemas.Token:
        user = await self.user_repo.get_by_username_or_email(
            username_or_email=username_email
        )
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        return schemas.Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_tokens(self, refresh_token: str) -> schemas.Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = decode_access_token(refresh_token)
            token_type: str | None = payload.get("type")
            user_id_str: str | None = payload.get("sub")

            if token_type != "refresh" or user_id_str is None:
                raise credentials_exception

            user_id = int(user_id_str)
        except (jwt.PyJWTError, ValueError) as err:
            raise credentials_exception from err

        user = await self.user_repo.get_by_id(user_id=user_id)
        if user is None or not user.is_active:
            raise credentials_exception

        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return schemas.Token(
            access_token=new_access_token, refresh_token=new_refresh_token
        )
