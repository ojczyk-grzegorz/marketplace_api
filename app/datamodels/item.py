import datetime as dt
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field

from app.datamodels.user import UserDBOut


class Item(BaseModel):
    search: str | None = None
    category: str | None = None
    subcategory: list[str] | None = None
    price: tuple[Decimal, Decimal] = Field(
        default=(Decimal("0.01"), Decimal("100_000_000.0")), min_items=2, max_items=2
    )
    brand: str | None = None
    features: dict | None = None


class ItemDBToList(BaseModel):
    item_id: uuid.UUID | None = None
    name: str | None = None
    category: str | None = None
    price: float | None = None
    brand: str | None = None
    features: dict | None = None


class ItemDBSingle(BaseModel):
    item_id: uuid.UUID | None = None
    name: str | None = None
    category: str | None = None
    subcategories: list[str] | None = None
    price: float | None = None
    brand: str | None = None
    features: dict | None = None
    description: str


class ItemDB(ItemDBToList):
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None

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


class QueryItemMultiple(BaseModel):
    q: Item
    items: list[ItemDBToList]


class QueryItemSingle(BaseModel):
    item_id: uuid.UUID
    item: ItemDBSingle
