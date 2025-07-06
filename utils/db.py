from typing import Any
import os
import psycopg2
import json
from numbers import Number
import time
import json
import datetime as dt

from utils.configs import Settings, get_settings


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


def get_filter(column: str, value: Any):
    if isinstance(value, list):
        flt = f"{column} IN ({', '.join(parse_value_to_sql(x) for x in value)})"
    elif isinstance(value, tuple):
        flt = f"{column} BETWEEN {parse_value_to_sql(value[0])} AND {parse_value_to_sql(value[1])}"
    else:
        flt = f"{column} = {parse_value_to_sql(value)}"
    return flt


def db_query(query: str, log_kwargs: dict = {}) -> list[tuple]:
    settings: Settings = get_settings()
    start = time.perf_counter_ns()

    with psycopg2.connect(
        host=settings.database.host,
        port=settings.database.port,
        user=settings.database.user,
        password=settings.database.password,
        database=settings.database.database,
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        try:
            results = cursor.fetchall()
        except psycopg2.ProgrammingError:
            results = []

    duration_ms = (time.perf_counter_ns() - start) / 1_000_000
    if log_kwargs:
        log = {
            "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "query_details": log_kwargs,
        }
        timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
        with open(
            os.path.join("logs", "logs_query", timestamp + ".log"), "a"
        ) as log_file:
            log_file.write("\n" + json.dumps(log, ensure_ascii=False))
    return results


def db_search_simple(
    table: str,
    columns: list[str],
    where: str = "",
    other: str = "",
    log_kwargs: dict = {},
) -> list[dict]:
    where = f"WHERE {where}" if where else ""
    query = f"SELECT {', '.join(columns)} FROM {table} {where} {other}"
    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns, x)) for x in results]


def db_search_user_by_id(
    table: str, user_id: int, columns: list[str], log_kwargs: dict = {}
) -> dict | None:
    users = db_search_simple(
        table=table,
        columns=columns,
        where=f"uid = {user_id}",
        other="LIMIT 1",
        log_kwargs=log_kwargs,
    )
    return users[0] if users else None


def db_insert(
    table: str,
    data: dict | list[dict],
    columns_out: list[str],
    log_kwargs: dict = {},
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
    """
    if columns_out and isinstance(columns_out, str):
        query += f" RETURNING {columns_out}"
    elif columns_out and isinstance(columns_out, list):
        query += f" RETURNING {', '.join(columns_out)}"

    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns_out, result)) for result in results]


def db_update(
    table: str,
    data: dict,
    where: str,
    columns_out: list[str],
    log_kwargs: dict = {},
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


def db_remove(table: str, where: str, columns_out: list[str], log_kwargs: dict = {}):
    query = f"""
        DELETE FROM {table}
        WHERE {where}
        RETURNING {", ".join(columns_out)}
    """

    results = db_query(query, log_kwargs=log_kwargs)
    return [dict(zip(columns_out, result)) for result in results]
