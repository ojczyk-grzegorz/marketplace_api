import datetime as dt
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone: str
    first_name: str
    last_name: str
    birth_date: dt.date
    country: str
    city: str
    street: str
    street_number: str
    postal_code: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: dt.date | None = None
    country: str | None = None
    city: str | None = None
    street: str | None = None
    street_number: str | None = None
    postal_code: str | None = None


class UserDBIn(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: dt.date | None = None
    country: str | None = None
    city: str | None = None
    street: str | None = None
    street_number: str | None = None
    postal_code: str | None = None

    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    password_hash: str | None = None


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
