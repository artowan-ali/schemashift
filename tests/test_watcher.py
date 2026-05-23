"""Tests for schemashift.watcher."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemashift.watcher import watch, WatchResult


# ---------------------------------------------------------------------------
# Fixtures – minimal SQL schema files
# ---------------------------------------------------------------------------

BEFORE_SQL = """
CREATE TABLE users (
    id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100)
);
"""

AFTER_SQL = """
CREATE TABLE users (
    id INTEGER NOT NULL,
    name VARCHAR(100)
);
"""

AFTER_ADDCOL_SQL = """
CREATE TABLE users (
    id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    nickname VARCHAR(50)
);
"""


@pytest.fixture()
def before_file(tmp_path: Path) -> Path:
    p = tmp_path / "before.sql"
    p.write_text(BEFORE_SQL)
    return p


@pytest.fixture()
def after_file(tmp_path: Path) -> Path:
    p = tmp_path / "after.sql"
    p.write_text(AFTER_SQL)
    return p


@pytest.fixture()
def after_addcol_file(tmp_path: Path) -> Path:
    p = tmp_path / "after_add.sql"
    p.write_text(AFTER_ADDCOL_SQL)
    return p


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_watch_returns_watch_result(before_file: Path, after_file: Path) -> None:
    result = watch(before_file, after_file)
    assert isinstance(result, WatchResult)


def test_watch_detects_breaking_change(before_file: Path, after_file: Path) -> None:
    result = watch(before_file, after_file)
    assert result.has_breaking_changes is True


def test_watch_non_breaking_no_flag(before_file: Path, after_addcol_file: Path) -> None:
    result = watch(before_file, after_addcol_file)
    assert result.has_breaking_changes is False


def test_watch_no_export_dir_returns_empty_paths(before_file: Path, after_file: Path) -> None:
    result = watch(before_file, after_file)
    assert result.exported_paths == []


# ---------------------------------------------------------------------------
# Export behaviour
# ---------------------------------------------------------------------------

def test_watch_exports_json_when_dir_given(before_file: Path, after_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "reports"
    result = watch(before_file, after_file, export_dir=out, fmt="json")
    assert len(result.exported_paths) == 1
    assert result.exported_paths[0].suffix == ".json"
    assert result.exported_paths[0].exists()


def test_watch_exports_markdown_when_requested(before_file: Path, after_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "reports"
    result = watch(before_file, after_file, export_dir=out, fmt="markdown")
    assert result.exported_paths[0].suffix == ".md"


def test_watch_exports_summary_when_flag_set(before_file: Path, after_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "reports"
    result = watch(before_file, after_file, export_dir=out, export_summary=True)
    paths = {p.name for p in result.exported_paths}
    assert "summary.json" in paths


def test_watch_summary_json_valid(before_file: Path, after_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "reports"
    watch(before_file, after_file, export_dir=out, export_summary=True)
    data = json.loads((out / "summary.json").read_text())
    assert "breaking" in data
    assert "total" in data
