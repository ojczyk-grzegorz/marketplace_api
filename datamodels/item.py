import datetime as dt
from pydantic import BaseModel, Field

from datamodels.user import UserDBOut


class ItemDBToList(BaseModel):
    iid: int | None = None
    iid_uuid4: str | None = None

    name: str | None = None
    seller_id: int | None = None
    price: float | None = None

    category: str | None = None
    type: str | None = None
    style: str | None = None
    brand: str | None = None
    condition: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: float | None = None

    width: str | None = None
    fastener: str | None = None
    heel: str | None = None
    toe: str | None = None

    country: str | None = None
    city: str | None = None

    icon: str | None = None


class ItemDB(ItemDBToList):
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None

    images: list[str] = []
    description: str | None = None


class QueryItems(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
    )

    price: tuple[float, float] = (0.01, 1_000_000.0)

    category: list[str] | None = None
    type: str | None = None
    style: list[str] | None = None
    brand: list[str] | None = None
    condition: list[str] | None = None
    material: list[str] | None = None
    color: list[str] | None = None
    pattern: list[str] | None = None
    size: list[float] | None = None

    width: list[str] | None = None
    fastener: list[str] | None = None
    heel: list[str] | None = None
    toe: list[str] | None = None

    country: list[str] | None = None
    city: list[str] | None = None


class ItemsUser(BaseModel):
    user: UserDBOut
    items: list[ItemDBToList]


class ItemsQuery(BaseModel):
    q: QueryItems
    items: list[ItemDBToList]


class ItemCreate(BaseModel):
    name: str
    price: float

    category: str | None = None
    type: str | None = None
    style: str | None = None
    brand: str | None = None
    condition: str
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: float | None = None

    width: str | None = None
    fastener: str | None = None
    heel: str | None = None
    toe: str | None = None

    country: str
    city: str

    expires_at: dt.datetime

    icon: str | None = None
    images: list[str] = []
    description: str | None = None


class ItemUpdate(ItemCreate):
    iid: int

    name: str | None = None
    price: float | None = None

    condition: str | None = None

    city: str | None = None
    street: str | None = None

    expires_at: dt.datetime | None = None

    icon: str | None = None
    images: list[str] | None = None
    description: str | None = None


class ItemRemove(BaseModel):
    item_id: int
