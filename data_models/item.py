import datetime as dt
from pydantic import BaseModel, ConfigDict


class ItemPrice(BaseModel):
    model_config=ConfigDict(extra="allow")
    
    _id: str | None = None
    _id_currency: str | None = None

    currency: str
    base_100: int
    tax_100: int

class ItemPost(BaseModel):
    model_config=ConfigDict(extra="allow")

    _id: str | None = None
    description: str | None = None
    post: str | None = None

class ItemFeature(BaseModel):
    model_config=ConfigDict(extra="ignore")

    _id: str | None = None
    name: str
    value: str | int | float | None

class ItemCategory(BaseModel):
    model_config=ConfigDict(extra="ignore")

    _id: str | None = None
    name: str

class ItemSubCategory(BaseModel):
    model_config=ConfigDict(extra="ignore")

    _id: str | None = None
    name: str

class Item(BaseModel):
    _id: str | None = None
    datetime: dt.datetime = dt.datetime.now()
    name: str
    price: ItemPrice
    post: ItemPost
    features: list[ItemFeature]
    categories: list[ItemCategory]
    subcategories: list[ItemSubCategory]
