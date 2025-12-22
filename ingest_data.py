import json

from sqlalchemy import text

from app.utils.configs import get_settings
from app.utils.db import get_db_session


def main():
    settings = get_settings()
    db = next(get_db_session())

    with open("postgres/db_setup/CREATE_TABLES.sql") as f:
        db.execute(text(f.read()))
        db.commit()

    with open("postgres/db_setup/items.json") as f:
        items = json.load(f)
        items = [{**item, "features": json.dumps(item["features"])} for item in items]

    db.execute(
        text("TRUNCATE " + settings.db_table_items + " RESTART IDENTITY CASCADE;")
    )
    db.execute(
        text(
            "INSERT INTO"
            + " "
            + settings.db_table_items
            + " (item_id, name, category, subcategories, price, brand, description, created_at, updated_at, features)"
            " VALUES (:item_id, :name, :category, :subcategories, :price, :brand, :description, :created_at, :updated_at, :features);"
        ),
        params=items,
    )
    db.commit()


if __name__ == "__main__":
    main()
