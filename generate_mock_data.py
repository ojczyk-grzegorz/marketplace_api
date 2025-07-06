import random
from datetime import datetime, timedelta, timezone
import json
import os
from uuid import uuid4

import psycopg2

from utils.auth import get_password_hash

from db.mock_data.mock_values.common import CITIES, STREETS
from db.mock_data.mock_values.users import FIRST_NAMES, LAST_NAMES
from db.mock_data.mock_values.items import (
    CATEGORIES,
    TYPES,
    STYLES,
    BRANDS,
    CONDITIONS,
    MATERIALS,
    COLORS,
    PATTERNS,
    WIDTHS,
    FASTENERS,
    HEELS,
    TOES,
    DESCRIPTIONS,
)


dir_files_db = "db/mock_data"
os.makedirs(dir_files_db, exist_ok=True)

filepath_users = os.path.join(dir_files_db, "users.json")
filepath_items = os.path.join(dir_files_db, "items.json")
filepath_transactions = os.path.join(dir_files_db, "transactions.json")

today = datetime(2025, 6, 11, tzinfo=timezone.utc)
six_months_ago = today - timedelta(days=180)


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)


def main():
    random.seed(0)

    ########### USERS ###########
    user_count = 33
    users = []
    n = 0
    for first_name in FIRST_NAMES:
        for last_name in LAST_NAMES:
            created_at = random_date(six_months_ago, today)
            user = dict(
                uid=n + 1,
                uid_uuid4=uuid4().hex,
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone=f"+48{random.randint(500000000, 799999999)}",
                password_hash=get_password_hash("password"),
                first_name=first_name,
                last_name=last_name,
                birth_date=random_date(
                    datetime(1975, 1, 1), datetime(2009, 12, 31)
                ).strftime("%Y-%m-%d"),
                country="PL",
                city=random.choice(CITIES),
                street=random.choice(STREETS),
                street_number=str(random.randint(1, 200)),
                postal_code=f"{random.randint(10, 99)}-{random.randint(100, 999)}",
                created_at=created_at.isoformat(),
                updated_at=created_at.isoformat(),
            )
            users.append(user)
            n += 1
            if n >= user_count:
                break
        if n >= user_count:
            break

    ########### ITEMS ###########
    items = []
    for n in range(70):
        seller = users[random.randint(0, len(users) // 3)]

        brand = random.choice(BRANDS)
        category = random.choice(CATEGORIES)
        material = random.choice(MATERIALS)
        color = random.choice(COLORS)

        features = dict(
            type=random.choice(TYPES),
            style=random.choice(STYLES),
            condition=random.choice(CONDITIONS),
            pattern=random.choice(PATTERNS),
            size=float(random.randint(30, 60)),
            width=random.choice(WIDTHS),
            fastener=random.choice(FASTENERS),
            heel=random.choice(HEELS),
            toe=random.choice(TOES),
        )

        created_at = random_date(datetime.fromisoformat(seller["created_at"]), today)

        joins_sent = ["\n", ".\n", ". "]
        joins_kv = [" ", " ", ": ", ":", " - ", "-"]
        join_kv: str = random.choice(joins_kv)
        join_sent: str = random.choice(joins_sent)
        desc = list(set(random.choices(DESCRIPTIONS, k=random.randint(2, 6))))
        feat = list(set(random.choices(list(features.items()), k=len(desc) - 1)))
        description = []
        for d, f in zip(desc, feat):
            (description.append(d),)
            description.append(join_kv.join([str(x) for x in f]))
        description.append(desc[-1])
        description = join_sent.join(description)

        item = dict(
            iid=n + 1,
            iid_uuid4=uuid4().hex,
            name=f"{brand} {color} {material} {category}",
            seller_id=seller["uid"],
            price=float(random.randint(10, 300)),
            brand=brand,
            category=category,
            material=material,
            color=color,
            **features,
            country=seller["country"],
            city=seller["city"],
            created_at=created_at.isoformat(),
            updated_at=created_at.isoformat(),
            expires_at=(
                created_at + timedelta(days=random.randint(15, 60))
            ).isoformat(),
            icon=None,
            images=[],
            description=description,
        )
        items.append(item)

    ########### TRANSACTIONS ###########
    transactions = []
    for n in range(30):
        item: dict = items.pop()

        for user in users:
            if user["uid"] == item["seller_id"]:
                seller = user
                break

        while True:
            buyer = random.choice(users)
            if buyer != seller:
                break

        sold_at = random_date(
            datetime.fromisoformat(item["created_at"]),
            today,
        )
        finilized = random_date(
            sold_at,
            today,
        ).isoformat()
        transaction = dict(
            tid=n + 1,
            tid_uuid4=uuid4().hex,
            sold_at=sold_at.isoformat(),
            item=item,
            seller_uid_uuid4=seller["uid_uuid4"],
            buyer_uid_uuid4=buyer["uid_uuid4"],
            seller_snapshot=seller,
            buyer_snapshot=buyer,
            finilized=random.choice([finilized, finilized, finilized, finilized, None]),
        )
        transactions.append(transaction)

    with open(filepath_users, "w") as file:
        json.dump(users, file, indent=4)
    print("Users generated:", len(users))

    with open(filepath_items, "w") as file:
        json.dump(items, file, indent=4)
    print("Items generated:", len(items))

    with open(filepath_transactions, "w") as file:
        json.dump(transactions, file, indent=4)
    print("Archived transactions generated:", len(transactions))

    with open("db/postgres/database.json", "r") as file:
        database_config = json.load(file)

    recreate_tables(database_config, "db/postgres/CREATE_TABLES.sql")

    insert_table_json(
        database_config,
        "db/mock_data/users.json",
        remove=[
            "uid",
        ],
    )
    insert_table_json(
        database_config,
        "db/mock_data/transactions.json",
        remove=["tid", "tid_uuid4"],
    )
    insert_table_json(
        database_config,
        "db/mock_data/items.json",
        remove=[
            "iid",
        ],
    )


def recreate_tables(db_config: dict, create_tables_sql: str = "CREATE_TABLES.sql"):
    with open(create_tables_sql, "r") as file:
        create_tables_query = file.read()

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        cursor.execute(create_tables_query)
        connection.commit()


def insert_table_json(db_config: dict, filepath: str, remove: list[str] = []):
    with open(filepath, "r") as file:
        data: list[dict] = json.load(file)
    for key in remove:
        for item in data:
            if key in item:
                del item[key]

    columns = ", ".join(data[0].keys())
    data_json = json.dumps(data).replace("'", "''")
    table_name = filepath.split("/")[-1].split(".")[0]

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO {table_name} ({columns})
            SELECT {columns}
            FROM json_populate_recordset(
                NULL::{table_name},
                '{data_json}'
            )
            RETURNING *;
        """)
        connection.commit()


if __name__ == "__main__":
    main()
