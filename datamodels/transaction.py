import datetime as dt
from pydantic import BaseModel, Field
from typing import Literal

from datamodels.item import ItemDB
from datamodels.user import UserDB


class TransactionCurrentDB(BaseModel):
    tid: int
    tid_uuid4: str

    buyer_id: int
    status: Literal["pending", "finished", "cancelled", "expired"]

    transaction_start: dt.datetime
    transaction_end: dt.datetime | None = None


class TransactionCurrentOut(BaseModel):
    transaction: TransactionCurrentDB
    item: ItemDB


class TransationArchivedDB(BaseModel):
    tid_uuid4: str
    status: Literal["finished", "cancelled", "expired"]
    transaction_start: dt.datetime
    transaction_end: dt.datetime
    item_id_uuid4: str
    item_snapshot: ItemDB
    buyer_id_uuid4: str
    buyer_snapshot: UserDB
    seller_id_uuid4: str
    seller_snapshot: UserDB
