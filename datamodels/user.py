import datetime as dt
from pydantic import BaseModel, EmailStr


class Address(BaseModel):
    type: str = ""
    country: str | None = None
    city: str | None = None
    street: str | None = None
    street_number: str | None = None
    postal_code: str | None = None


class Review(BaseModel):
    rating: float
    comment: str
    created_at: dt.datetime


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    phone: str
    first_name: str
    last_name: str
    birth_date: str
    country: str
    city: str
    street: str
    street_number: str
    postal_code: str


class UserDb(UserCreate):
    uid: int
    created_at: dt.datetime
    updated_at: dt.datetime
    addresses: list[Address] = []
    reviews: list[Review] = []
    rating: float = 0.0
    avatar: str | None = None
    last_activity: dt.datetime


class UserPatch(BaseModel):
    uid: int
    email: EmailStr | None = None
    password_hash: str | None = None
    phone: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: str | None = None
    country: str | None = None
    city: str | None = None
    street: str | None = None
    street_number: str | None = None
    postal_code: str | None = None
    addresses: list[Address] | None = None
    avatar: str | None = None


class UserOut(BaseModel):
    email: EmailStr
    phone: str
    first_name: str
    last_name: str
    country: str
    city: str
    created_at: dt.datetime
    reviews: list[Review] | None = None
    rating: float = 0.0
    avatar: str | None = None
    last_activity: dt.datetime
