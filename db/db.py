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


def db_search(query: str):
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
    return results


def db_insert(table: str, data: dict, columns_out: list[str]):
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)
    
    columns_insert_sql = ", ".join(data.keys())
    data_json = json.dumps(data, ensure_ascii=False)
    data_json = data_json.replace("'", "''")

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        query = f"""
            INSERT INTO {table} ({columns_insert_sql})
                SELECT {columns_insert_sql}
                FROM json_populate_record(
                    NULL::{table},
                    '{data_json}'
                )
            RETURNING {", ".join(columns_out)}
        """
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
    return dict(zip(columns_out, results[0]))


def parse_to_update(data: dict) -> str:
    parsed_data = ""
    for key, value in data.items():
        if isinstance(value, str):
            value = "'" + value.replace("'", "''") + "'"
        elif value is None:
            value = "NULL"
        elif isinstance(value, Number):
            value = str(value)
        else:
            value = "'" + json.dumps(value, ensure_ascii=False).replace("'", "''") + "'"
        parsed_data += f"{key} = {value}, "
    return parsed_data[:-2]  # Remove the last comma and space


def db_update(table: str, data: dict, where: str):
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)

    data: str = parse_to_update(data)
    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        query = f"""
            UPDATE {table}
            SET {data}
            WHERE {where}
            RETURNING row_to_json({table});
        """
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
    return results


def db_remove(table: str, where: str):
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)

    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        query = f"""
            DELETE FROM {table}
            WHERE {where}
            RETURNING row_to_json({table});
        """
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
    return results
