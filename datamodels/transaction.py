import datetime as dt
from pydantic import BaseModel


class TransactionCreate(BaseModel):
    item_id: int


class TransactionDBIn(BaseModel):
    sold_at: dt.datetime
    item: dict
    seller_uid_uuid4: str
    buyer_uid_uuid4: str
    seller_snapshot: dict
    buyer_snapshot: dict
    finilized: dt.datetime | None = None


class TransactionDBOut(BaseModel):
    tid: int
    tid_uuid4: str
    sold_at: dt.datetime
    item: dict
    seller_uid_uuid4: str
    buyer_uid_uuid4: str
    finilized: dt.datetime | None = None


class TransactionFinilize(BaseModel):
    transaction_id: int
