import datetime as dt
from decimal import Decimal
import uuid

from pydantic import BaseModel


class TransactionToCreate(BaseModel):
    item_ids: dict[str, int]
    delivery_option_id: str
    discount_codes: list[str] = []
    name: str
    last_name: str
    email: str
    phone: str
    country: str
    city: str
    postal_code: str
    address_line_1: str
    address_line_2: str | None = None


class TransactionCreated(BaseModel):
    transaction_id: uuid.UUID
    user_id: uuid.UUID
    created_at: dt.datetime
    delivery_option: str
    delivery_price: Decimal
    total_price: Decimal
    name: str
    last_name: str
    email: str
    phone: str
    country: str
    city: str
    postal_code: str
    address_line_1: str
    address_line_2: str | None = None


class TransactionItem(BaseModel):
    item_id: uuid.UUID
    name: str
    price_unit: Decimal
    price_after_discounts: Decimal
    count: int
    applied_discounts: list[dict] = []


class TransactionAction(BaseModel):
    action: str
    performed_at: dt.datetime
    description: str | None = None


class ResponseGetCurrentTransaction(BaseModel):
    transaction: TransactionCreated
    items: list[TransactionItem]
    actions: list[TransactionAction] = []


class ResponseGetAllCurrentTransactions(BaseModel):
    transactions: list[ResponseGetCurrentTransaction]
