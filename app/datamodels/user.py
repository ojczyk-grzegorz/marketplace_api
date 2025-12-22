import datetime as dt
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str = Field(..., exclude=True)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str | None = Field(None, exclude=True)


class UserDBIn(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: UUID = Field(default_factory=lambda: uuid4())
    email: EmailStr
    phone: str
    created_at: dt.datetime
    updated_at: dt.datetime
    password_hash: str


class UserDBOut(BaseModel):
    uid: int | None = None
    uid_uuid4: str | None = None

    email: EmailStr | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    country: str | None = None
    city: str | None = None

    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


class UserDBOutDetailed(UserDBOut):
    birth_date: dt.date | None = None
    street: str | None = None
    street_number: str | None = None
    postal_code: str | None = None
