import random
from datetime import datetime, timedelta, timezone
import json
import os
from uuid import uuid4

import psycopg2

from mock_values.common import CITIES, STREETS
from mock_values.users import FIRST_NAMES, LAST_NAMES
from mock_values.transactions import STATUS
from mock_values.items import (
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
    DESCRIPTIONS
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

    ########### USERS ###########
    users = []
    n = 0
    for first_name in FIRST_NAMES:
        for last_name in LAST_NAMES:
            created_at = random_date(six_months_ago, today)
            user = {
                "uid": n + 1,
                "uid_uuid4": uuid4().hex,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "phone": f"+48{random.randint(500000000, 799999999)}",
                "password_hash": "password_hash",
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
                "created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                "updated_at": created_at.strftime("%Y-%m-%dT%H:%M:%S")
            }
            n += 1
            users.append(user)

    ########### CATEGORIES ###########
    categories = []
    for n, name in enumerate(CATEGORIES):
        categories.append(
            {
                "cid": n + 1,
                "name": name,
            }
        )
    
    ########### TYPES ###########
    types = []
    for n, name in enumerate(TYPES):
        types.append(
            {
                "tid": n + 1,
                "name": name,
            }
        )
    ########### STYLES ###########
    styles = []
    for n, name in enumerate(STYLES):
        styles.append(
            {
                "sid": n + 1,
                "name": name,
            }
        )
    ########### BRANDS ###########
    brands = []
    for n, name in enumerate(BRANDS):
        brands.append(
            {
                "bid": n + 1,
                "name": name,
            }
        )
    ########### CONDITIONS ###########
    conditions = []
    for n, name in enumerate(CONDITIONS):
        conditions.append(
            {
                "cid": n + 1,
                "name": name,
            }
        )
    ########### MATERIALS ###########
    materials = []
    for n, name in enumerate(MATERIALS):
        materials.append(
            {
                "mid": n + 1,
                "name": name,
            }
        )
    ########### COLORS ###########
    colors = []
    for n, name in enumerate(COLORS):
        colors.append(
            {
                "cid": n + 1,
                "name": name,
            }
        )
    ########### PATTERNS ###########
    patterns = []
    for n, name in enumerate(PATTERNS):
        patterns.append(
            {
                "pid": n + 1,
                "name": name,
            }
        )
    ########### WIDTHS ###########
    widths = []
    for n, name in enumerate(WIDTHS):
        widths.append(
            {
                "wid": n + 1,
                "name": name,
            }
        )
    ########### FASTENERS ###########
    fasteners = []
    for n, name in enumerate(FASTENERS):
        fasteners.append(
            {
                "fid": n + 1,
                "name": name,
            }
        )
    ########### HEELS ###########
    heels = []
    for n, name in enumerate(HEELS):
        heels.append(
            {
                "hid": n + 1,
                "name": name,
            }
        )
    ########### TOES ###########
    toes = []
    for n, name in enumerate(TOES):
        toes.append(
            {
                "tid": n + 1,
                "name": name,
            }
        )


    ########### ITEMS ###########
    items = []
    for n in range(5_000):
        seller=users[random.randint(0, len(users) // 3)],

        brand = random.choice(brands)
        category = random.choice(categories)
        material = random.choice(materials)
        color = random.choice(colors)

        created_at = random_date(six_months_ago, today)

        joins_sent = ["\n", ".\n", ". "]
        joins_kv = [" ", " ", ": ", ":", " - ", "-"]
        join_kv: str = random.choice(joins_kv)
        join_sent: str = random.choice(joins_sent)
        desc = list(set(random.choices(DESCRIPTIONS, k=random.randint(2, 6))))
        feat = list(
            set(random.choices(list(features_specific.items()), k=len(desc) - 1))
        )
        description = []
        for d, f in zip(desc, feat):
            (description.append(d),)
            description.append(join_kv.join([str(x) for x in f]))
        description.append(desc[-1])
        description = join_sent.join(description)

        item = dict(
            iid=n+1,
            iid_uuid4=uuid4().hex,
            name=f"{brand["name"]} {color["name"]} {material["name"]} {category["name"]}",
            seller_id=seller["uid"],
            transaction_id=None,
            price=float(random.randint(10, 300)),
            category_id=category["cid"],
            type_id=random.choice(types)["tid"],
            style_id=random.choice(styles)["sid"],
            brand_id=random.choice(brands)["bid"],
            condition_id=random.choice(conditions)["cid"],
            material_id=random.choice(materials)["mid"],
            color_id=random.choice(colors)["cid"],
            pattern_id=random.choice(patterns)["pid"],
            size=float(random.randint(30, 60)),
            
            width_id=random.choice(widths)["wid"],
            fastener_id=random.choice(fasteners)["fid"],
            heel_id=random.choice(heels)["hid"],
            toe_id=random.choice(toes)["tid"],
            
            country=seller["country"],
            city=seller["city"],
            
            created_at=created_at.isoformat(),
            updated_at=created_at.isoformat(),
            expires_at=(created_at + timedelta(days=random.randint(15, 60))).isoformat()

            icon=None,
            images=[],
            description=description,
        )
        items.append(item)


    ########### STATUS ###########
    status = []
    for n, s in enumerate(STATUS):
        status.append(
            {
                "sid": n + 1,
                "name": s,
            }
        )

    ########### TRANSACTIONS active ###########
    transactions_active = []
    for n in range(4_000):
        item: dict = items[n]

        while True:
            user = random.choice(users)
            if user["uid"] != item["seller_id"]:
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
            "buyer_id": user["uid"],
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
