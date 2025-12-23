from decimal import Decimal
import uuid
import datetime as dt

from pydantic import BaseModel


class DetailsUserCreate(BaseModel):
    email: str | None = None
    phone: str | None = None


class ResponseUserCreate(BaseModel):
    message: str = "User created successfully"
    details: DetailsUserCreate


class DetailsUserUpdate(DetailsUserCreate):
    password_changed: bool = False


class ResponseUserUpdate(BaseModel):
    message: str = "User updated successfully"
    details: DetailsUserUpdate


class DetailsUserRemove(DetailsUserCreate):
    pass


class ResponseUserRemove(BaseModel):
    message: str = "User removed successfully"
    details: DetailsUserRemove


class ResponseSingleItem(BaseModel):
    item_id: uuid.UUID
    name: str
    category: str
    subcategories: list[str] | None = None
    price: Decimal
    brand: str | None = None
    description: str | None = None
    features: dict | None = None
    stock: int


class ResponseGetSingleItem(BaseModel):
    item: ResponseSingleItem


class ResponseQueryItem(BaseModel):
    item_id: uuid.UUID
    name: str
    category: str
    subcategories: list[str] | None = None
    price: Decimal
    brand: str | None = None
    features: dict | None = None
    stock: int


class ResponseGetMultipleItems(BaseModel):
    items: list[ResponseQueryItem]


class ResponseTransactionDetails(BaseModel):
    transaction_id: uuid.UUID
    user_id: uuid.UUID
    created_at: dt.datetime
    delivery_option: str
    delivery_price: Decimal
    delivery_details: dict
    total_price: Decimal


class ResponseTransactionItem(BaseModel):
    item_id: uuid.UUID
    name: str
    price_unit: Decimal
    price_after_discounts: Decimal
    count: int
    appied_discounts: list[dict] = []


class ResponseTransaction(BaseModel):
    transaction: ResponseTransactionDetails
    items: list[ResponseTransactionItem]
