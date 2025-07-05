import psycopg2
import json
from numbers import Number
import time
import json
import datetime as dt

from utils.logs import logger


def parse_value_to_sql(value) -> str:
    if isinstance(value, Number):
        value = str(value)
    elif isinstance(value, str):
        value = "'" + value.replace("'", "''") + "'"
    elif value is None:
        value = "NULL"
    else:
        value = "'" + json.dumps(value, ensure_ascii=False).replace("'", "''") + "'"
    if value == "''":
        value = "NULL"
    return value


def db_query(query: str, log_kwargs: dict | None = None) -> list[tuple]:
    with open("db/postgres/database.json", "r") as f:
        db_config = json.load(f)

    start = time.perf_counter_ns()
    with psycopg2.connect(**db_config) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        results = cursor.fetchall()
    duration_ms = (time.perf_counter_ns() - start) / 1_000_000
    if isinstance(log_kwargs, str):
        log = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            **log_kwargs,
        }
        logger.info(json.dumps(log, ensure_ascii=False))
    return results


def db_search_simple(
    table: str,
    columns: list[str],
    where: str = "",
    other: str = "",
    log_kwargs: dict | None = None,
) -> list[dict]:
    where = f"WHERE {where}" if where else ""
    query = f"SELECT {', '.join(columns)} FROM {table} {where} {other}"
    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns, x)) for x in results]


def db_insert(
    table: str,
    data: dict | list[dict],
    columns_out: list[str],
    log_kwargs: dict | None = None,
):
    columns = []
    values = []

    if not isinstance(data, list):
        data = [data]

    for column in data[0]:
        columns.append(column)

    for obj in data:
        value = ", ".join(
            parse_value_to_sql(obj.get(column, None)) for column in columns
        )
        values.append(f"({value})")

    query = f"""
        INSERT INTO {table} ({", ".join(columns)})
        VALUES {", ".join(values)}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns_out, result)) for result in results]


def db_update(
    table: str,
    data: dict,
    where: str,
    columns_out: list[str],
    log_kwargs: dict | None = None,
):
    data = ", ".join(f"{k} = {parse_value_to_sql(v)}" for k, v in data.items())

    query = f"""
        UPDATE {table}
        SET {data}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns_out, result)) for result in results]


def db_remove(
    table: str, where: str, columns_out: list[str], log_kwargs: dict | None = None
):
    query = f"""
        DELETE FROM {table}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns_out, result)) for result in results]
