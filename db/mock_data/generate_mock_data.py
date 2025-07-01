import random
from datetime import datetime, timedelta, timezone
import json
import os
from uuid import uuid4

import psycopg2

from mock_values.common import CITIES, STREETS
from mock_values.users import FIRST_NAMES, LAST_NAMES, USER_REVIEWS
from mock_values.transactions import STATUS
from mock_values.items import (
    CATEGORIES,
    SIZES,
    STYLES,
    CONDITIONS,
    MATERIALS,
    COLORS,
    BRANDS,
    PATTERNS,
    DESCRIPTIONS,
    DELIVERIES,
)


dir_files_db = "db/mock_data"
os.makedirs(dir_files_db, exist_ok=True)

filepath_users = os.path.join(dir_files_db, "users.json")
filepath_categories = os.path.join(dir_files_db, "categories.json")
filepath_status = os.path.join(dir_files_db, "status.json")
filepath_items = os.path.join(dir_files_db, "items.json")
filepath_transactions_active = os.path.join(dir_files_db, "transactions_active.json")
filepath_transactions_archived = os.path.join(
    dir_files_db, "transactions_archived.json"
)

today = datetime(2025, 6, 11, tzinfo=timezone.utc)
six_months_ago = today - timedelta(days=180)


# Helper function to generate random dates for history
def random_date(start_date, end_date):
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    return start_date + timedelta(days=random_days)


def main():
    random.seed(0)

    ########### CUSTOMERS ###########
    users = []
    n = 0
    for first_name in FIRST_NAMES:
        for last_name in LAST_NAMES:
            reviews = list(set(random.choices(USER_REVIEWS, k=random.randint(0, 20))))
            created_at = random_date(six_months_ago, today)
            customer = {
                "uid": n + 1,
                "uid_uuid4": uuid4().hex,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "password_hash": "password_hash",
                "phone": f"+48{random.randint(500000000, 799999999)}",
                "first_name": first_name,
                "last_name": last_name,
                "birth_date": random_date(
                    datetime(1975, 1, 1), datetime(2009, 12, 31)
                ).strftime("%Y-%m-%d"),
                "country": "PL",
                "city": random.choice(CITIES),
                "street": random.choice(STREETS),
                "street_number": str(random.randint(1, 200)),
                "postal_code": f"{random.randint(10, 99)}-{random.randint(100, 999)}",
                "addresses": [],
                "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "updated_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "last_activity": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "reviews": [
                    {
                        "rating": review[0],
                        "comment": review[1],
                        "created_at": random_date(created_at, today).strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        ),
                    }
                    for review in reviews
                ],
                "rating": round(sum(review[0] for review in reviews) / len(reviews), 1)
                if reviews
                else 0.0,
                "avatar": None,
            }
            n += 1
            users.append(customer)

    ########### CATEGORIES ###########
    categories = []
    for n, category in enumerate(CATEGORIES):
        categories.append(
            {
                "cid": n + 1,
                "name": category,
            }
        )

    ########### STATUS ###########
    status = []
    for n, s in enumerate(STATUS):
        status.append(
            {
                "sid": n + 1,
                "name": s,
            }
        )

    ########### ITEMS ###########
    items = []
    for n in range(5_000):
        iid = n + 1

        category = random.choice(categories)
        seller = users[random.randint(0, len(users) // 3)]
        subcategory = random.choice(CATEGORIES[category["name"]])

        price = float(random.randint(1, 300))
        condition = random.choice(CONDITIONS)
        brand = random.choice(BRANDS)
        material = random.choice(MATERIALS)
        color = random.choice(COLORS)
        pattern = random.choice(PATTERNS)
        size = random.choice(SIZES)
        style = random.choice(STYLES)

        features_common = {}
        for feature, values in subcategory.get("features_common", {}).items():
            features_common[feature] = random.choice(values)

        features_specific = {}
        for feature, values in subcategory.get("features_specific", {}).items():
            features_specific[feature] = random.choice(values)

        features = {
            **features_common,
            **features_specific,
        }

        created_at = random_date(six_months_ago, today)
        updated_at = created_at
        expires_at = created_at + timedelta(days=random.randint(15, 60))

        name = f"{brand} {color} {subcategory['name']}"

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

        item = {
            "iid": iid,
            "iid_uuid4": uuid4().hex,
            "name": name,
            "category_id": category["cid"],
            "seller_id": seller["uid"],
            "seller_rating": seller["rating"],
            "transaction_id": None,
            "subcategory": subcategory["name"],
            "price": price,
            "condition": condition,
            "brand": brand,
            "material": material,
            "color": color,
            "pattern": pattern,
            "size": size,
            "style": style,
            "features_specific": features_specific,
            "city": seller["city"],
            "street": seller["street"],
            "delivery": list(
                set(random.choices(DELIVERIES, k=random.randint(1, len(DELIVERIES))))
            ),
            "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "updated_at": updated_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%S"),
            "icon": None,
            "images": [],
            "interested": random.randint(0, 30),
            "description": description,
            **features_common,
        }

        items.append(item)

    ########### TRANSACTIONS active ###########
    transactions_active = []
    for n in range(4_000):
        item: dict = items[n]

        while True:
            customer = random.choice(users)
            if customer["uid"] != item["seller_id"]:
                break

        transaction_start = random_date(
            datetime.fromisoformat(item["created_at"]),
            datetime.fromisoformat(item["expires_at"]),
        )
        stat = random.choice(status)
        if stat["name"] not in ["active", "shipping", "disputed"]:
            transaction_end = random_date(
                transaction_start,
                datetime.fromisoformat(item["expires_at"]),
            )
        else:
            transaction_end = None

        transaction = {
            "tid": n + 1,
            "tid_uuid4": uuid4().hex,
            "buyer_id": customer["uid"],
            "status_id": stat["sid"],
            "transaction_start": transaction_start.strftime("%Y-%m-%dT%H:%M:%S"),
            "transaction_end": transaction_end.strftime("%Y-%m-%dT%H:%M:%S")
            if transaction_end
            else None,
        }
        transactions_active.append(transaction)
        item["transaction_id"] = transaction["tid"]

    ########### TRANSACTIONS FINISHED ###########
    transactions_archived = []
    # for n in range(len(items) - 1, -1, -1):
    #     item: dict = items[n]
    #     transaction_id = item["transaction_id"]
    #     if transaction_id is None:
    #         continue

    #     for tn, transaction in enumerate(transactions_active):
    #         if transaction["tid"] == transaction_id:
    #             break

    #     if transaction["transaction_end"] is None:
    #         continue

    #     transaction.pop("tid", None)

    #     transaction["item_id_uuid4"] = item["iid_uuid4"]
    #     transaction["item_snapshot"] = item

    #     for user in users:
    #         if user["uid"] == transaction["buyer_id"]:
    #             transaction["buyer_id_uuid4"] = user["uid_uuid4"]
    #             transaction["buyer_snapshot"] = user
    #             transaction.pop("buyer_id", None)
    #             break

    #     for user in users:
    #         if user["uid"] == item["seller_id"]:
    #             transaction["seller_id_uuid4"] = user["uid_uuid4"]
    #             transaction["seller_snapshot"] = user
    #             break

    #     transactions_archived.append(transaction)
    # items.pop(n)
    # transactions_active.pop(tn)

    with open(filepath_users, "w") as file:
        json.dump(users, file, indent=4)
    print("Users generated:", len(users))

    with open(filepath_categories, "w") as file:
        json.dump(categories, file, indent=4)
    print("Categories generated:", len(categories))

    with open(filepath_status, "w") as file:
        json.dump(status, file, indent=4)
    print("Status generated:", len(status))

    with open(filepath_items, "w") as file:
        json.dump(items, file, indent=4)
    print("Items generated:", len(items))

    with open(filepath_transactions_archived, "w") as file:
        json.dump(transactions_archived, file, indent=4)
    print("Archived transactions generated:", len(transactions_archived))

    with open(filepath_transactions_active, "w") as file:
        json.dump(transactions_active, file, indent=4)
    print("Active transactions generated:", len(transactions_active))

    with open("db/postgres/database.json", "r") as file:
        database_config = json.load(file)

    recreate_tables(database_config, "db/postgres/CREATE_TABLES.sql")

    insert_table_json(
        database_config, "db/mock_data/users.json", remove=["uid", "uid_uuid4"]
    )
    insert_table_json(database_config, "db/mock_data/categories.json", remove=["cid"])
    insert_table_json(database_config, "db/mock_data/status.json", remove=["sid"])
    insert_table_json(
        database_config,
        "db/mock_data/transactions_active.json",
        remove=["tid", "tid_uuid4"],
    )
    insert_table_json(
        database_config, "db/mock_data/items.json", remove=["iid", "iid_uuid4"]
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
