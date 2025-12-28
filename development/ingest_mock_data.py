import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
from sqlmodel import insert, text

def main():
    db = next(get_db_session())

    with open("postgres/CREATE_TABLES.sql") as f:
        db.exec(text(f.read()))
    
    for model in [
        DBDiscount,
        DBGroundStaff,
        DBDeliveryOptions,
        DBItem,
        DBUser,
        DBItemSnapshot,
        DBTransaction,
        DBTransactionAction,
        DBTransactionItem,
        DBTransactionDiscount,
        DBTransactionFinalized,
    ]:
        with open(f"development/mock_data/{model.__name__}.json") as f:
            values = json.load(f)
            if values:
                query = insert(model).values(values)
                db.exec(query)
    db.commit()


if __name__ == "__main__":
    main()
