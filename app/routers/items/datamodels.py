from decimal import Decimal
from typing import Annotated
import uuid

from pydantic import BaseModel, Field


class ItemQuery(BaseModel):
    search: Annotated[str | None, Field(default=None)]
    category: Annotated[str | None, Field(default=None)]
    subcategory: Annotated[list[str] | None, Field(default=None)]
    price: Annotated[
        tuple[Decimal, Decimal],
        Field(default=(Decimal("0.01"), Decimal("100_000_000.0")), min_length=2, max_length=2),
    ]
    brand: Annotated[str | None, Field(default=None)]
    features: Annotated[dict | None, Field(default=None)]


class ItemFiltered(BaseModel):
    item_id: Annotated[uuid.UUID, Field(...)]
    name: Annotated[str, Field(...)]
    category: Annotated[str, Field(...)]
    subcategories: Annotated[list[str] | None, Field(default=None)]
    price: Annotated[Decimal, Field(...)]
    brand: Annotated[str | None, Field(default=None)]
    features: Annotated[dict | None, Field(default=None)]
    stock: Annotated[int, Field(...)]


class ItemRetrieved(BaseModel):
    item_id: Annotated[uuid.UUID, Field(...)]
    name: Annotated[str, Field(...)]
    category: Annotated[str, Field(...)]
    subcategories: Annotated[list[str] | None, Field(default=None)]
    price: Annotated[Decimal, Field(...)]
    brand: Annotated[str | None, Field(default=None)]
    description: Annotated[str | None, Field(default=None)]
    features: Annotated[dict | None, Field(default=None)]
    stock: Annotated[int, Field(...)]


class ResponseFilterItems(BaseModel):
    items: Annotated[list[ItemFiltered], Field(...)]


class ResponseRetrieveItem(BaseModel):
    item: Annotated[ItemRetrieved, Field(...)]
