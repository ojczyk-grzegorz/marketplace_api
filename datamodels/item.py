import datetime as dt
from pydantic import BaseModel, Field

from datamodels.user import UserOut


class ItemDB(BaseModel):
    iid: int | None = None
    iid_uuid4: str | None = None

    name: str | None = None
    category_id: int | None = None

    seller_id: int | None = None
    seller_rating: float = 0.0

    subcategory: str | None = None

    price: float | None = None
    condition: str | None = None
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features_specific: dict | None = None

    city: str | None = None
    street: str | None = None
    delivery: list[str] = []

    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None

    icon: str | None = None
    images: list[str] = []
    interested: int = 0
    description: str | None = None


class QueryItems(BaseModel):
    limit: int = Field(
        default=20,
        ge=1,
        le=50,
    )
    subcategory: list[str] | None = None
    brand: list[str] | None = None
    material: list[str] | None = None
    color: list[str] | None = None
    pattern: list[str] | None = None
    size: list[str] | None = None
    style: list[str] | None = None
    price: tuple[float, float] = (0.01, 1_000_000.0)
    features_specific: dict | None = None


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
    features_specific: dict | None = None

    city: str
    delivery: list[str] = Field(min_length=1)

    icon: str | None = None


class ItemsUser(BaseModel):
    user: UserOut
    items: list[ItemDBToList]


class ItemsQuery(BaseModel):
    q: QueryItems
    items: list[ItemDBToList]


class ItemCreate(BaseModel):
    name: str
    category_id: int

    subcategory: str | None = None

    price: float
    condition: str
    brand: str | None = None
    material: str | None = None
    color: str | None = None
    pattern: str | None = None
    size: str | None = None
    style: str | None = None
    features_specific: dict | None = None

    city: str
    street: str
    delivery: list[str] = Field(min_length=1)

    expires_at_days: int

    icon: str | None = None
    images: list[str] = []
    description: str | None = None


class ItemCreated(BaseModel):
    seller: UserOut
    item: ItemDB


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
    features_specific: dict | None = None

    city: str | None = None
    street: str | None = None
    delivery: list[str] = []

    expires_at_days: int | None = None

    icon: str | None = None
    images: list[str] = []
    description: str | None = None


class ItemsRemove(BaseModel):
    item_ids: list[int]
