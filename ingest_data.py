import json

from sqlmodel import text, delete, insert

from app.utils.configs import get_settings
from app.utils.db import get_db_session_sql_model
from app.dbmodels.dbmodels import (
    DBUser,
    DBItem,
    DBDiscount,
    DBGroundStaff,
    DBDeliveryOptions,
)


def main():
    db = next(get_db_session_sql_model())

    with open("postgres/db_setup/CREATE_TABLES.sql") as f:
        db.exec(text(f.read()))

    with open("postgres/db_setup/users.json") as f:
        users = json.load(f)
        query = insert(DBUser).values(users)
        db.exec(query)

    with open("postgres/db_setup/items.json") as f:
        items = json.load(f)
        query = insert(DBItem).values(items)
        db.exec(query)

    with open("postgres/db_setup/discounts.json") as f:
        discounts = json.load(f)
        query = insert(DBDiscount).values(discounts)
        db.exec(query)

    with open("postgres/db_setup/ground_staff.json") as f:
        ground_staff = json.load(f)
        query = insert(DBGroundStaff).values(ground_staff)
        db.exec(query)

    with open("postgres/db_setup/delivery_options.json") as f:
        delivery_options = json.load(f)
        query = insert(DBDeliveryOptions).values(delivery_options)
        db.exec(query)
    db.commit()


if __name__ == "__main__":
    main()
