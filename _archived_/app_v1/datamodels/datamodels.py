from enum import Enum
from decimal import Decimal
import datetime as dt
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class RequestTypeItemGet(str, Enum):
    details = "details"
    stocks = "stocks"


class RequestTypeItemPut(str, Enum):
    details = "details"
    stocks = "stocks"


class Price(BaseModel):
    date: str
    price: Decimal | None = None


class ItemDetail(BaseModel):
    iid: int | None = None
    name: str | None = None
    prices: list[Price] = []
    category: str | None = None
    brand: str | None = None
    rating: Decimal | None = None


class Shipment(BaseModel):
    date: str
    quantity: int
    status: str
    destination: str


class Location(BaseModel):
    quantity: int
    location: str
    aisle: str | None = None
    shelf: str | None = None
    details: dict | None = None


class ItemStock(BaseModel):
    iid: int | None = None
    shipments: list[Shipment] = []
    locations: list[Location] = []


class Customer(BaseModel):
    cid: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    country: str | None = None
    city: str | None = None
    street_name: str | None = None
    street_number: str | None = None
    postal_code: str | None = None


class TransactionRequest(BaseModel):
    cid: int | None = None
    iid: int | None = None
    quantity: int | None = None


class Transaction(TransactionRequest):
    tid: int | None = None
    timestamp: dt.datetime | None = None
    # price: Decimal | None = None
    # status: str | None = None


# TODO: NOT USED YET!!!
# https://ihateregex.io/expr/url/
class Image(BaseModel):
    id: UUID
    url: str = Field(
        ...,
        # pattern="https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%_\+.~#?&\/\/=]*)",
    )
    url2: HttpUrl
    name: str
