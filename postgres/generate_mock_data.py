import random
import json
import os
import sys

base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

from app.utils.configs import get_settings
from app.utils.db import db_query, db_insert
from postgres.utils.utils import get_mock_users, get_mock_items, get_mock_transactions

DIR = "postgres"

dir_mock_data = os.path.join(DIR, "mock_data")
os.makedirs(dir_mock_data, exist_ok=True)
filepath_mock_data = os.path.join(dir_mock_data, "mock_data.json")


def main():
    random.seed(0)

    ########### USERS ###########
    users = get_mock_users(
        user_count=33,
    )
    print("Users generated:", len(users))

    ########### ITEMS ###########
    items = get_mock_items(
        item_count=70,
        users=users,
    )
    print("Items generated:", len(items))

    ########### TRANSACTIONS ###########
    transactions = get_mock_transactions(
        transaction_count=30,
        users=users,
        items=items,
    )
    print("Archived transactions generated:", len(transactions))

    with open(filepath_mock_data, "w") as file:
        json.dump(
            dict(users=users, items=items, transactions=transactions), file, indent=4
        )

    with open(os.path.join(DIR, "db_setup", "CREATE_TABLES.sql"), "r") as file:
        create_tables_query = file.read()

    db_query(create_tables_query, log_kwargs={})

    settings = get_settings()
    for user in users:
        user.pop("uid")
    for item in items:
        item.pop("iid")
    for transaction in transactions:
        transaction.pop("tid")
    db_insert(settings.database.tables.users.name, users, columns_out=[], log_kwargs={})

    db_insert(settings.database.tables.items.name, items, columns_out=[], log_kwargs={})

    db_insert(
        settings.database.tables.transactions.name,
        transactions,
        columns_out=[],
        log_kwargs={},
    )


if __name__ == "__main__":
    main()
