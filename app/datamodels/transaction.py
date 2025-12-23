import uuid

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    item_ids: dict[str, int]
    delivery_option_id: uuid.UUID
    discount_codes: list[str] = []
