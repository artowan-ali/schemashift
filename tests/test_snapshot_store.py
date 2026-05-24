"""Tests for schemashift.snapshot_store."""

import pytest

from schemashift.models import Schema, Table, Column
from schemashift.snapshot import create_snapshot
from schemashift.snapshot_store import SnapshotStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schema() -> Schema:
    col = Column(name="id", col_type="INTEGER", nullable=False)
    table = Table(name="orders", columns={"id": col})
    return Schema(tables={"orders": table})


def _store(tmp_path):
    return SnapshotStore(store_dir=tmp_path / "snapshots")


# ---------------------------------------------------------------------------
# save / exists / load
# ---------------------------------------------------------------------------

def test_save_creates_file(tmp_path):
    store = _store(tmp_path)
    snap = create_snapshot(_schema(), label="v1")
    path = store.save(snap)
    assert path.exists()


def test_exists_true_after_save(tmp_path):
    store = _store(tmp_path)
    snap = create_snapshot(_schema(), label="v1")
    store.save(snap)
    assert store.exists("v1")


def test_exists_false_before_save(tmp_path):
    store = _store(tmp_path)
    assert not store.exists("v1")


def test_load_returns_correct_label(tmp_path):
    store = _store(tmp_path)
    snap = create_snapshot(_schema(), label="v1")
    store.save(snap)
    loaded = store.load("v1")
    assert loaded.label == "v1"


def test_load_missing_raises(tmp_path):
    store = _store(tmp_path)
    with pytest.raises(FileNotFoundError):
        store.load("ghost")


# ---------------------------------------------------------------------------
# list_labels
# ---------------------------------------------------------------------------

def test_list_labels_empty_store(tmp_path):
    store = _store(tmp_path)
    assert store.list_labels() == []


def test_list_labels_returns_saved_labels(tmp_path):
    store = _store(tmp_path)
    for label in ("alpha", "beta", "gamma"):
        store.save(create_snapshot(_schema(), label=label))
    assert store.list_labels() == ["alpha", "beta", "gamma"]


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

def test_delete_removes_file(tmp_path):
    store = _store(tmp_path)
    store.save(create_snapshot(_schema(), label="v1"))
    store.delete("v1")
    assert not store.exists("v1")


def test_delete_returns_false_when_missing(tmp_path):
    store = _store(tmp_path)
    assert store.delete("nope") is False


# ---------------------------------------------------------------------------
# latest
# ---------------------------------------------------------------------------

def test_latest_returns_none_when_empty(tmp_path):
    store = _store(tmp_path)
    assert store.latest() is None


def test_latest_returns_a_snapshot(tmp_path):
    store = _store(tmp_path)
    store.save(create_snapshot(_schema(), label="first"))
    result = store.latest()
    assert result is not None
    assert result.label == "first"
