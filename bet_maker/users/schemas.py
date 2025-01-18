from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    name: Optional[str] = None
    username: Optional[int] = None
    email: Optional[int] = None
    password: Optional[str] = None


class UserDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    create_date: int
    update_date: int
