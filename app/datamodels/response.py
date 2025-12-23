import datetime as dt
from decimal import Decimal
import uuid

from pydantic import BaseModel


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


class ResponseTransactionAction(BaseModel):
    action: str
    performed_at: dt.datetime
    description: str | None = None


class ResponseTransaction(BaseModel):
    transaction: ResponseTransactionDetails
    items: list[ResponseTransactionItem]
    actions: list[ResponseTransactionAction] = []


class ResponseTransactionsCurrent(BaseModel):
    transactions: list[ResponseTransaction]
