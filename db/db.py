import json
import os

dir_files_db = os.path.dirname(os.path.abspath(__file__))

filepath_items = os.path.join(dir_files_db, "mock_data", "items.json")
filepath_items_clothes = os.path.join(dir_files_db, "mock_data", "items_clothes.json")
filepath_items_shoes = os.path.join(dir_files_db, "mock_data", "items_shoes.json")

filepath_users = os.path.join(dir_files_db, "mock_data", "users.json")
filepath_transactions = os.path.join(dir_files_db, "mock_data", "transactions.json")

items: dict[str, list[dict]] = dict()
with open(filepath_items, "r") as f:
    items["items"] = json.load(f)
with open(filepath_items_clothes, "r") as f:
    items["items_clothes"] = json.load(f)
with open(filepath_items_shoes, "r") as f:
    items["items_shoes"] = json.load(f)

with open(filepath_users, "r") as f:
    users: list = json.load(f)

with open(filepath_transactions, "r") as f:
    transactions: list = json.load(f)

database = dict(
    items=items,
    users=users,
    transactions=transactions,
)
