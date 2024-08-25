from datetime import datetime
from typing import Optional

from shortuuid import ShortUUID
from sqlmodel import Field
from sqlmodel import SQLModel

s = ShortUUID(alphabet="0123456789")


def generate_suid():
    return s.random(length=21)


class UserBase(SQLModel):
    id: str = Field(primary_key=True, min_length=21, max_length=21)
    email: str = Field(unique=True, index=True)
    verified: bool = Field(default=False)
    picture: Optional[str] = Field(default=None)

    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)


class ActivityBase(SQLModel):
    type: str = Field(nullable=False)
    where: str = Field(nullable=False)
    source: str = Field(nullable=False)
    browser: Optional[str] = Field(default=None)


class ActivityCreate(ActivityBase):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Activity(ActivityBase, table=True):
    id: str = Field(default_factory=generate_suid, primary_key=True, min_length=21, max_length=21)

    created_at: datetime = Field(nullable=False)
    updated_at: datetime = Field(nullable=False)
