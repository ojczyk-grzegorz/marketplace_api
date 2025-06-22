import json
import os

dir_files_db = os.path.dirname(os.path.abspath(__file__))

filepath_items = os.path.join(dir_files_db, "mock_data", "items.json")

filepath_users = os.path.join(dir_files_db, "mock_data", "users.json")
filepath_transactions = os.path.join(dir_files_db, "mock_data", "transactions.json")

with open(filepath_items, "r") as f:
    items = json.load(f)

with open(filepath_users, "r") as f:
    users: list = json.load(f)

with open(filepath_transactions, "r") as f:
    transactions: list = json.load(f)

database = dict(
    items=items,
    users=users,
    transactions=transactions,
)
