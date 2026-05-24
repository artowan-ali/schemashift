"""Tests for schemashift.snapshot."""

import json
from pathlib import Path

import pytest

from schemashift.models import Schema, Table, Column
from schemashift.snapshot import (
    Snapshot,
    create_snapshot,
    snapshot_to_dict,
    save_snapshot,
    load_snapshot,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_schema() -> Schema:
    col = Column(name="id", col_type="INTEGER", nullable=False)
    table = Table(name="users", columns={"id": col})
    return Schema(tables={"users": table})


# ---------------------------------------------------------------------------
# create_snapshot
# ---------------------------------------------------------------------------

def test_create_snapshot_label():
    schema = _simple_schema()
    snap = create_snapshot(schema, label="v1")
    assert snap.label == "v1"


def test_create_snapshot_has_timestamp():
    schema = _simple_schema()
    snap = create_snapshot(schema, label="v1")
    assert snap.timestamp  # non-empty string


def test_create_snapshot_metadata_defaults_empty():
    schema = _simple_schema()
    snap = create_snapshot(schema, label="v1")
    assert snap.metadata == {}


def test_create_snapshot_metadata_passed_through():
    schema = _simple_schema()
    snap = create_snapshot(schema, label="v1", metadata={"env": "prod"})
    assert snap.metadata["env"] == "prod"


def test_snapshot_str_contains_label():
    schema = _simple_schema()
    snap = create_snapshot(schema, label="release-1")
    assert "release-1" in str(snap)


# ---------------------------------------------------------------------------
# snapshot_to_dict
# ---------------------------------------------------------------------------

def test_snapshot_to_dict_has_label():
    snap = create_snapshot(_simple_schema(), label="v2")
    d = snapshot_to_dict(snap)
    assert d["label"] == "v2"


def test_snapshot_to_dict_has_tables():
    snap = create_snapshot(_simple_schema(), label="v2")
    d = snapshot_to_dict(snap)
    assert "users" in d["tables"]


def test_snapshot_to_dict_column_type_preserved():
    snap = create_snapshot(_simple_schema(), label="v2")
    d = snapshot_to_dict(snap)
    assert d["tables"]["users"]["id"]["type"] == "INTEGER"


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_and_load_round_trip(tmp_path):
    snap = create_snapshot(_simple_schema(), label="round-trip")
    path = tmp_path / "snap.json"
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded.label == "round-trip"
    assert "users" in loaded.schema.tables


def test_save_creates_file(tmp_path):
    snap = create_snapshot(_simple_schema(), label="file-test")
    path = tmp_path / "snap.json"
    save_snapshot(snap, path)
    assert path.exists()


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "nonexistent.json")


def test_saved_file_is_valid_json(tmp_path):
    snap = create_snapshot(_simple_schema(), label="json-check")
    path = tmp_path / "snap.json"
    save_snapshot(snap, path)
    with path.open() as fh:
        data = json.load(fh)
    assert "tables" in data
