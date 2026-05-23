"""Unit tests for schemashift.parser."""

import pytest
from schemashift.parser import parse_schema, _parse_columns


SIMPLE_SQL = """
CREATE TABLE users (
    id INT NOT NULL,
    username VARCHAR(100),
    email VARCHAR(255) NOT NULL
);
"""

MULTI_TABLE_SQL = """
CREATE TABLE orders (
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    total DECIMAL(10,2)
);

CREATE TABLE products (
    product_id INT NOT NULL,
    name VARCHAR(200)
);
"""


def test_parse_single_table_name():
    schema = parse_schema(SIMPLE_SQL)
    assert "users" in schema


def test_parse_column_names():
    schema = parse_schema(SIMPLE_SQL)
    columns = schema["users"]["columns"]
    assert set(columns.keys()) == {"id", "username", "email"}


def test_parse_column_type():
    schema = parse_schema(SIMPLE_SQL)
    assert schema["users"]["columns"]["id"]["type"] == "INT"
    assert schema["users"]["columns"]["username"]["type"] == "VARCHAR"


def test_nullable_detection():
    schema = parse_schema(SIMPLE_SQL)
    assert schema["users"]["columns"]["id"]["nullable"] is False
    assert schema["users"]["columns"]["username"]["nullable"] is True


def test_parse_multiple_tables():
    schema = parse_schema(MULTI_TABLE_SQL)
    assert "orders" in schema
    assert "products" in schema


def test_parse_multiple_tables_columns():
    schema = parse_schema(MULTI_TABLE_SQL)
    assert "order_id" in schema["orders"]["columns"]
    assert "product_id" in schema["products"]["columns"]


def test_empty_sql_returns_empty_schema():
    schema = parse_schema("")
    assert schema == {}


def test_primary_key_constraint_skipped():
    sql = """
    CREATE TABLE items (
        id INT NOT NULL,
        name VARCHAR(50),
        PRIMARY KEY (id)
    );
    """
    schema = parse_schema(sql)
    columns = schema["items"]["columns"]
    assert "PRIMARY" not in columns
    assert "id" in columns
