import json
import os

dir_files_db = os.path.dirname(os.path.abspath(__file__))

filepath_items = os.path.join(dir_files_db, "mock_data", "items.json")
filepath_users = os.path.join(dir_files_db, "mock_data", "users.json")
filepath_transactions_current = os.path.join(
    dir_files_db, "mock_data", "transactions_current.json"
)
filepath_transactions_archived = os.path.join(
    dir_files_db, "mock_data", "transactions_archived.json"
)

with open(filepath_items, "r") as f:
    items = json.load(f)

with open(filepath_users, "r") as f:
    users: list = json.load(f)

with open(filepath_transactions_current, "r") as f:
    transactions_current: list = json.load(f)

with open(filepath_transactions_archived, "r") as f:
    transactions_archived: list = json.load(f)

database = dict(
    items=items,
    users=users,
    transactions_current=transactions_current,
    transactions_archived=transactions_archived,
)
