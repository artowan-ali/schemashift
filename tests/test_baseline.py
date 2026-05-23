"""Tests for schemashift.baseline module."""

import json
import os
import pytest

from schemashift.baseline import (
    save_baseline,
    load_baseline,
    baseline_exists,
    DEFAULT_BASELINE_PATH,
)
from schemashift.loader import load_schema_from_string


SAMPLE_DDL = """
CREATE TABLE users (
  id INTEGER NOT NULL,
  email VARCHAR(255),
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE orders (
  order_id INTEGER NOT NULL,
  amount DECIMAL
);
"""


@pytest.fixture()
def schema():
    return load_schema_from_string(SAMPLE_DDL)


@pytest.fixture()
def baseline_path(tmp_path):
    return str(tmp_path / "test_baseline.json")


def test_save_baseline_creates_file(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    assert os.path.exists(baseline_path)


def test_save_baseline_valid_json(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    with open(baseline_path) as fh:
        data = json.load(fh)
    assert "tables" in data


def test_save_baseline_contains_tables(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    with open(baseline_path) as fh:
        data = json.load(fh)
    assert "users" in data["tables"]
    assert "orders" in data["tables"]


def test_save_baseline_preserves_column_type(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    with open(baseline_path) as fh:
        data = json.load(fh)
    assert data["tables"]["users"]["columns"]["email"]["type"] == "VARCHAR(255)"


def test_save_baseline_preserves_nullable(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    with open(baseline_path) as fh:
        data = json.load(fh)
    assert data["tables"]["users"]["columns"]["id"]["nullable"] is False
    assert data["tables"]["users"]["columns"]["email"]["nullable"] is True


def test_load_baseline_returns_schema(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    loaded = load_baseline(path=baseline_path)
    assert "users" in loaded.tables
    assert "orders" in loaded.tables


def test_load_baseline_columns_match(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    loaded = load_baseline(path=baseline_path)
    assert "id" in loaded.tables["users"].columns
    assert "email" in loaded.tables["users"].columns


def test_load_baseline_file_not_found(baseline_path):
    with pytest.raises(FileNotFoundError):
        load_baseline(path=baseline_path)


def test_load_baseline_malformed_raises(tmp_path):
    bad_path = str(tmp_path / "bad.json")
    with open(bad_path, "w") as fh:
        json.dump({"wrong_key": {}}, fh)
    with pytest.raises(ValueError, match="Malformed baseline"):
        load_baseline(path=bad_path)


def test_baseline_exists_true(schema, baseline_path):
    save_baseline(schema, path=baseline_path)
    assert baseline_exists(path=baseline_path) is True


def test_baseline_exists_false(baseline_path):
    assert baseline_exists(path=baseline_path) is False
