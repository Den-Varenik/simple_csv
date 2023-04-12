from datetime import date
from typing import List, Optional

from pydantic import BaseModel
from app.schemas.categories import CategorySchema

class UserBase(BaseModel):
    firstname: str
    lastname: str
    email: str
    gender: str
    birthDate: date


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserPatch(UserBase):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    birthDate: Optional[date] = None
    categories: Optional[List[int]] = None


class UserSchema(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserWithCategories(UserSchema):
    categories: List[CategorySchema]
