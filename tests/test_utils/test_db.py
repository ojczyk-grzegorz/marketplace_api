import pytest
from unittest.mock import Mock

import psycopg2

from tests.test_utils.utils import CONFIGS_JSON

from app.utils.configs import Settings
from app.utils.db import (
    parse_value_to_sql,
    get_filter,
    db_query,
    db_search_simple,
    db_search_user_by_id,
    db_insert,
    db_update,
    db_remove,
)


@pytest.mark.parametrize(
    "value, expected",
    [
        (None, "NULL"),
        ("string", "'string'"),
        (123, "123"),
        (3.14, "3.14"),
        (True, "True"),
        (False, "False"),
        ([], "'[]'"),
        ([1, 2, 3], "'[1, 2, 3]'"),
        ({"key": "value"}, '\'{"key": "value"}\''),
        ({"key": "'value'"}, "'{\"key\": \"''value''\"}'"),
    ],
)
def test_parse_value_to_sql(value, expected):
    result = parse_value_to_sql(value)
    assert result == expected


@pytest.mark.parametrize(
    "column, value, expected",
    [
        ("name", "John", "name = 'John'"),
        ("age", 30, "age = 30"),
        ("is_active", True, "is_active = True"),
        ("tags", ["python", "testing"], "tags IN ('python', 'testing')"),
        ("balance", 123.45, "balance = 123.45"),
        ("created_at", None, "created_at = NULL"),
        ("price", (10.99, 20.99), "price BETWEEN 10.99 AND 20.99"),
    ],
)
def test_get_filter(mocker, column, value, expected):
    result = get_filter(column, value)
    assert result == expected


@pytest.mark.parametrize(
    "exception, results_expected, log_kwargs",
    [
        (None, [(1, "test"), (2, "example")], {}),
        (None, [(1, "test"), (2, "example")], {"extra": "data"}),
        (psycopg2.ProgrammingError, [], {}),
    ],
)
def test_db_query(mocker, exception, results_expected, log_kwargs):
    cursor = Mock()
    if not exception:
        cursor.fetchall.return_value = results_expected
    else:
        cursor.fetchall.side_effect = exception

    connection = Mock()
    connection.cursor.return_value = cursor

    file = Mock()

    mocker.patch("psycopg2.connect").return_value.__enter__.return_value = connection
    mocker.patch(
        "app.utils.db.get_settings"
    ).return_value = Settings.model_validate_json(CONFIGS_JSON)
    mocker.patch("builtins.open").return_value.__enter__.return_value = file

    query = "SELECT * FROM table"
    results = db_query(query, log_kwargs)

    connection.cursor.assert_called_once()
    cursor.execute.assert_called_once_with(query)
    connection.commit.assert_called_once()

    if log_kwargs:
        file.write.assert_called_once()

    assert results == results_expected


def test_db_search_simple(mocker):
    mock_db_query = mocker.patch("app.utils.db.db_query")

    table = "test_table"
    columns = ["id", "name"]
    where = "id > 0"
    other = "ORDER BY id"

    query = "SELECT id, name FROM test_table WHERE id > 0 ORDER BY id"
    log_kwargs = {}

    db_search_simple(table, columns, where, other, log_kwargs)
    mock_db_query.assert_called_once_with(query, log_kwargs=log_kwargs)


@pytest.mark.parametrize(
    "users_returned, expected",
    [
        (
            [{"id": 1, "name": "Alice", "email": "alice@example.com"}],
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
        ),
        ([], None),
    ],
)
def test_db_search_user_by_id(mocker, users_returned, expected):
    mock_db_search_simple = mocker.patch("app.utils.db.db_search_simple")
    mock_db_search_simple.return_value = users_returned

    table = "users"
    user_id = 1
    columns = ["id", "name", "email"]
    log_kwargs = {}

    users = db_search_user_by_id(table, user_id, columns, log_kwargs)
    mock_db_search_simple.assert_called_once_with(
        table=table,
        columns=columns,
        where=f"uid = {user_id}",
        other="LIMIT 1",
        log_kwargs=log_kwargs,
    )
    assert users == expected


def test_db_insert(mocker):
    results = [(1, "test")]
    results_expected = [{"id": 1, "name": "test"}]

    mock_db_query = mocker.patch("app.utils.db.db_query")
    mock_db_query.return_value = results

    table = "test_table"
    data = {"id": 1, "name": "test"}
    columns_out = ["id", "name"]
    log_kwargs = {}

    results = db_insert(table, data, columns_out, log_kwargs)

    query = """
        INSERT INTO test_table (id, name)
        VALUES (1, 'test')
     RETURNING id, name"""

    mock_db_query.assert_called_once_with(query, log_kwargs=log_kwargs)
    assert results == results_expected


def test_db_update(mocker):
    results = [(1, "updated")]
    results_expected = [{"id": 1, "name": "updated"}]

    mock_db_query = mocker.patch("app.utils.db.db_query")
    mock_db_query.return_value = results

    table = "test_table"
    data = {"id": 1, "name": "updated"}
    where = "id = 1"
    columns_out = ["id", "name"]
    log_kwargs = {}

    results = db_update(table, data, where, columns_out, log_kwargs)

    query = """
        UPDATE test_table
        SET id = 1, name = 'updated'
        WHERE id = 1
        RETURNING id, name
    """

    mock_db_query.assert_called_once_with(query, log_kwargs=log_kwargs)
    assert results == results_expected


def test_db_remove(mocker):
    mock_db_query = mocker.patch("app.utils.db.db_query")
    mock_db_query.return_value = [(1, "test")]

    table = "test_table"
    where = "id = 1"
    columns_out = ["id", "name"]
    log_kwargs = {}

    results = db_remove(table, where, columns_out, log_kwargs)

    query = """
        DELETE FROM test_table
        WHERE id = 1
        RETURNING id, name
    """
    mock_db_query.assert_called_once_with(query, log_kwargs=log_kwargs)
    assert results == [{"id": 1, "name": "test"}]
