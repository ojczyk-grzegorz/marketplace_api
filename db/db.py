import json
import os

dir_files_db = os.path.dirname(os.path.abspath(__file__))

filepath_items = os.path.join(dir_files_db, "mock_data", "items.json")
filepath_customers = os.path.join(dir_files_db, "mock_data", "customers.json")
filepath_transactions = os.path.join(dir_files_db, "mock_data", "transactions.json")

with open(filepath_items, "r") as f:
    items: list = json.load(f)

with open(filepath_customers, "r") as f:
    customers: list = json.load(f)

with open(filepath_transactions, "r") as f:
    transactions: list = json.load(f)

database = dict(
    items=items,
    customers=customers,
    transactions=transactions,
)
