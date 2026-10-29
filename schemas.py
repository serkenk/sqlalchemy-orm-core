# schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# --- POST SCHEMAS ---


class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    content: str = Field(..., min_length=1)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- USER SCHEMAS ---


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    posts: list[PostResponse] = []

    model_config = ConfigDict(from_attributes=True)
