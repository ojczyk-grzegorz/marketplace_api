import json
import uuid
from decimal import Decimal
import datetime as dt

from sqlmodel import select

from app.database.dbmodels import (
    DBDeliveryOptions,
    DBDiscount,
    DBGroundStaff,
    DBItem,
    DBUser,
    DBItemSnapshot,
    DBTransaction,
    DBTransactionAction,
    DBTransactionItem,
    DBTransactionDiscount,
    DBTransactionFinalized,
)
from app.database.utils import get_db_session


class JSONSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dt.datetime):
            return obj.isoformat()
        return super().default(obj)

def main():
    db = next(get_db_session())

    models = [
        DBDeliveryOptions,
        DBDiscount,
        DBGroundStaff,
        DBItem,
        DBUser,
        DBItemSnapshot,
        DBTransaction,
        DBTransactionAction,
        DBTransactionItem,
        DBTransactionDiscount,
        DBTransactionFinalized,
    ]

    for model in models:
        values = [value.model_dump() for value in db.exec(select(model))]
        with open(f"{model.__name__}.json", "w") as f:
            json.dump(values, f, indent=4, cls=JSONSerializer)


if __name__ == "__main__":
    main()
