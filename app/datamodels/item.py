from decimal import Decimal

from pydantic import BaseModel, Field


class Item(BaseModel):
    search: str | None = None
    category: str | None = None
    subcategory: list[str] | None = None
    price: tuple[Decimal, Decimal] = Field(
        default=(Decimal("0.01"), Decimal("100_000_000.0")), min_items=2, max_items=2
    )
    brand: str | None = None
    features: dict | None = None
