import psycopg2
import json
from numbers import Number


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
    where = f"WHERE {where}" if where else ""
    query = f"SELECT {', '.join(columns)} FROM {table} {where} {other}"
    results = db_query(query)
    return [dict(zip(columns, x)) for x in results]


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
    return [dict(zip(columns_out, result)) for result in results]


def db_update(table: str, data: dict, where: str, columns_out: list[str]):
    data = ", ".join(f"{k} = {parse_value_to_sql(v)}" for k, v in data.items())

    query = f"""
        UPDATE {table}
        SET {data}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query)
    return [dict(zip(columns_out, result)) for result in results]


def db_remove(table: str, where: str, columns_out: list[str]):
    query = f"""
        DELETE FROM {table}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query)
    return [dict(zip(columns_out, result)) for result in results]
