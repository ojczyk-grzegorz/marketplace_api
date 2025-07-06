import random
import json
import os

from utils.configs import get_settings
from utils.db import db_query, db_insert
from postgres.utils import get_mock_users, get_mock_items, get_mock_transactions


DIR_MOCK_DATA = "postgres/mock_data"
os.makedirs(DIR_MOCK_DATA, exist_ok=True)

filepath_users = os.path.join(DIR_MOCK_DATA, "users.json")
filepath_items = os.path.join(DIR_MOCK_DATA, "items.json")
filepath_transactions = os.path.join(DIR_MOCK_DATA, "transactions.json")


def main():
    random.seed(0)

    ########### USERS ###########
    users = get_mock_users(
        user_count=33,
    )

    ########### ITEMS ###########
    items = get_mock_items(
        item_count=70,
        users=users,
    )
    

    ########### TRANSACTIONS ###########
    transactions = get_mock_transactions(
        transaction_count=30,
        users=users,
        items=items,
    )
    
    print("Users generated:", len(users))
    with open(filepath_users, "w") as file:
        json.dump(users, file, indent=4)
    
    print("Items generated:", len(items))
    with open(filepath_items, "w") as file:
        json.dump(items, file, indent=4)

    print("Archived transactions generated:", len(transactions))
    with open(filepath_transactions, "w") as file:
        json.dump(transactions, file, indent=4)

    with open("postgres/CREATE_TABLES.sql", "r") as file:
        create_tables_query = file.read()

    db_query(
        create_tables_query,
        log_kwargs={}
    )

    settings = get_settings()
    db_insert(
        settings.database.tables.users.name,
        users,
        columns_out=[],
        log_kwargs={}
    )

    db_insert(
        settings.database.tables.items.name,
        items,
        columns_out=[],
        log_kwargs={}
    )

    db_insert(
        settings.database.tables.transactions.name,
        transactions,
        columns_out=[],
        log_kwargs={}
    )

if __name__ == "__main__":
    main()
