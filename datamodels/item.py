import datetime as dt
from pydantic import BaseModel, Field


class ItemDB(BaseModel):
    iid: int
    name: str
    cid: int

    seller_id: int
    seller_rating: float = 0.0

    subcategory: str | None = None

    price: float
    condition: str
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features: dict | None = None

    city: str
    street: str
    delivery: list[str] = Field(min_length=1)

    created_at: dt.datetime
    updated_at: dt.datetime
    expires_at: dt.datetime

    icon: str | None = None
    images: list[str] = []
    interested: int = 0
    description: str | None = None


class QueryItems(BaseModel):
    limit: int = Field(
        default=10,
        ge=1,
        le=30,
    )
    subcategory: list[str] | None = None
    brand: list[str] | None = None
    material: list[str] | None = None
    color: list[str] | None = None
    pattern: list[str] | None = None
    size: list[str] | None = None
    style: list[str] | None = None
    price: tuple[float, float] = (0.01, 1_000_000.0)
    features: dict | None = None


class ItemDBToList(BaseModel):
    iid: int
    name: str

    seller_rating: float = 0.0

    subcategory: str | None = None

    price: float
    condition: str
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features: dict | None = None

    city: str
    delivery: list[str] = Field(min_length=1)

    icon: str | None = None


class ItemsUser(BaseModel):
    user_id: int
    items: list[ItemDBToList]


class ItemsQuery(BaseModel):
    q: QueryItems
    items: list[ItemDBToList]


class ItemCreate(BaseModel):
    name: str
    cid: int

    subcategory: str | None = None

    price: float
    condition: str
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features: dict | None = None

    city: str
    street: str
    delivery: list[str] = Field(min_length=1)

    expires_at_days: int

    icon: str | None = None
    images: list[str] = []
    description: str | None = None


class ItemsCreate(BaseModel):
    seller_id: int
    items: list[ItemCreate]


class ItemsCreated(BaseModel):
    seller_id: int
    items: list[ItemDB]


class ItemUpdate(BaseModel):
    iid: int

    name: str | None = None

    subcategory: str | None = None

    price: float | None = None
    condition: str | None = None
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features: dict | None = None

    city: str | None = None
    street: str | None = None
    delivery: list[str] | None = None

    expires_at_days: int | None = None

    icon: str | None = None
    images: list[str] | None = None
    description: str | None = None
