"""Unit tests for schemashift.loader."""

import pytest
from pathlib import Path
from schemashift.loader import load_schema_from_file, load_schema_from_string


VALID_SQL = """
CREATE TABLE accounts (
    account_id INT NOT NULL,
    owner VARCHAR(100)
);
"""


def test_load_from_string_returns_schema():
    schema = load_schema_from_string(VALID_SQL)
    assert "accounts" in schema


def test_load_from_string_columns_present():
    schema = load_schema_from_string(VALID_SQL)
    assert "account_id" in schema["accounts"]["columns"]


def test_load_from_string_raises_on_no_tables():
    with pytest.raises(ValueError, match="No CREATE TABLE"):
        load_schema_from_string("SELECT 1;")


def test_load_from_file(tmp_path: Path):
    sql_file = tmp_path / "schema.sql"
    sql_file.write_text(VALID_SQL, encoding="utf-8")
    schema = load_schema_from_file(sql_file)
    assert "accounts" in schema


def test_load_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_schema_from_file("/nonexistent/path/schema.sql")


def test_load_from_file_raises_on_empty_sql(tmp_path: Path):
    sql_file = tmp_path / "empty.sql"
    sql_file.write_text("-- just a comment", encoding="utf-8")
    with pytest.raises(ValueError):
        load_schema_from_file(sql_file)
