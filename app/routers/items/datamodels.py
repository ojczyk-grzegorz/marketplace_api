from decimal import Decimal
import uuid

from pydantic import BaseModel, Field


class ItemQuery(BaseModel):
    search: str | None = None
    category: str | None = None
    subcategory: list[str] | None = None
    price: tuple[Decimal, Decimal] = Field(
        default=(Decimal("0.01"), Decimal("100_000_000.0")), min_items=2, max_items=2
    )
    brand: str | None = None
    features: dict | None = None


class ItemFiltered(BaseModel):
    item_id: uuid.UUID
    name: str
    category: str
    subcategories: list[str] | None = None
    price: Decimal
    brand: str | None = None
    features: dict | None = None
    stock: int


class ItemRetrieved(BaseModel):
    item_id: uuid.UUID
    name: str
    category: str
    subcategories: list[str] | None = None
    price: Decimal
    brand: str | None = None
    description: str | None = None
    features: dict | None = None
    stock: int


class ResponseFilterItems(BaseModel):
    items: list[ItemFiltered]


class ResponseRetrieveItem(BaseModel):
    item: ItemRetrieved
