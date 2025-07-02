import psycopg2
import json
import os

from numbers import Number

dir_files_db = os.path.dirname(os.path.abspath(__file__))

filepath_items = os.path.join(dir_files_db, "mock_data", "items.json")
filepath_users = os.path.join(dir_files_db, "mock_data", "users.json")
filepath_transactions_active = os.path.join(
    dir_files_db, "mock_data", "transactions_active.json"
)
filepath_transactions_archived = os.path.join(
    dir_files_db, "mock_data", "transactions_archived.json"
)

with open(filepath_items, "r") as f:
    items = json.load(f)

with open(filepath_users, "r") as f:
    users: list = json.load(f)

with open(filepath_transactions_active, "r") as f:
    transactions_active: list = json.load(f)

with open(filepath_transactions_archived, "r") as f:
    transactions_archived: list = json.load(f)

database = dict(
    items=items,
    users=users,
    transactions_active=transactions_active,
    transactions_archived=transactions_archived,
)


def parse_value_to_sql(value) -> str:
    if isinstance(value, Number):
        value = str(value)
    elif isinstance(value, str):
        value = "'" + value.replace("'", "''") + "'"
    elif value is None:
        value = "NULL"
    else:
        value = "'" + json.dumps(value, ensure_ascii=False).replace("'", "''") + "'"
    return value


def db_query(query: str):
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
    return results


def db_search_simple(
    table: str, columns: list[str], where: str = "", other: str = ""
) -> list[dict]:
    query = f"SELECT {', '.join(columns)} FROM {table} WHERE {where} {other}"
    results = db_query(query)
    return [dict(zip(columns, x)) for x in results] if results else []


def db_insert(table: str, data: dict, columns_out: list[str]):
    columns = []
    values = []
    for k, v in data.items():
        columns.append(k)
        values.append(parse_value_to_sql(v))

    query = f"""
        INSERT INTO {table} ({", ".join(columns)})
        VALUES ({", ".join(values)})
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query)
    return dict(zip(columns_out, results[0])) if results else None


def db_update(table: str, data: dict, where: str, columns_out: list[str]):
    data = ", ".join(f"{k} = {parse_value_to_sql(v)}" for k, v in data.items())

    query = f"""
        UPDATE {table}
        SET {data}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query)
    return dict(zip(columns_out, results[0])) if results else None


def db_remove(table: str, where: str, columns_out: list[str]):
    query = f"""
        DELETE FROM {table}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query)
    return [dict(zip(columns_out, result)) for result in results] if results else None
