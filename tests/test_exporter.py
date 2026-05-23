"""Tests for schemashift.exporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemashift.exporter import export_diff, export_summary_json
from schemashift.models import ChangeType, SchemaChange, SchemaDiff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(*changes: SchemaChange) -> SchemaDiff:
    return SchemaDiff(changes=list(changes))


def _breaking_change() -> SchemaChange:
    return SchemaChange(
        change_type=ChangeType.COLUMN_REMOVED,
        table="users",
        column="email",
        detail="column removed",
    )


def _non_breaking_change() -> SchemaChange:
    return SchemaChange(
        change_type=ChangeType.COLUMN_ADDED,
        table="users",
        column="nickname",
        detail=None,
    )


# ---------------------------------------------------------------------------
# export_diff – JSON
# ---------------------------------------------------------------------------

def test_export_json_creates_file(tmp_path: Path) -> None:
    dest = tmp_path / "out" / "diff.json"
    result = export_diff(_make_diff(_breaking_change()), dest, fmt="json")
    assert result == dest
    assert dest.exists()


def test_export_json_content_is_valid_json(tmp_path: Path) -> None:
    dest = tmp_path / "diff.json"
    export_diff(_make_diff(_breaking_change()), dest, fmt="json")
    data = json.loads(dest.read_text())
    assert isinstance(data, dict)


def test_export_json_contains_changes(tmp_path: Path) -> None:
    dest = tmp_path / "diff.json"
    export_diff(_make_diff(_breaking_change()), dest, fmt="json")
    data = json.loads(dest.read_text())
    assert "changes" in data
    assert len(data["changes"]) == 1


# ---------------------------------------------------------------------------
# export_diff – Markdown
# ---------------------------------------------------------------------------

def test_export_markdown_creates_file(tmp_path: Path) -> None:
    dest = tmp_path / "diff.md"
    result = export_diff(_make_diff(_non_breaking_change()), dest, fmt="markdown")
    assert result == dest
    assert dest.exists()


def test_export_markdown_contains_table_header(tmp_path: Path) -> None:
    dest = tmp_path / "diff.md"
    export_diff(_make_diff(_breaking_change()), dest, fmt="md")
    content = dest.read_text()
    assert "|" in content


# ---------------------------------------------------------------------------
# export_diff – invalid format
# ---------------------------------------------------------------------------

def test_export_invalid_format_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_diff(_make_diff(), tmp_path / "out.xml", fmt="xml")


# ---------------------------------------------------------------------------
# export_summary_json
# ---------------------------------------------------------------------------

def test_export_summary_creates_file(tmp_path: Path) -> None:
    dest = tmp_path / "summary.json"
    result = export_summary_json(_make_diff(_breaking_change()), dest)
    assert result == dest
    assert dest.exists()


def test_export_summary_counts_correct(tmp_path: Path) -> None:
    dest = tmp_path / "summary.json"
    export_summary_json(_make_diff(_breaking_change(), _non_breaking_change()), dest)
    data = json.loads(dest.read_text())
    assert data["total"] == 2
    assert data["breaking"] == 1
    assert data["non_breaking"] == 1
    assert data["has_breaking_changes"] is True


def test_export_summary_no_breaking(tmp_path: Path) -> None:
    dest = tmp_path / "summary.json"
    export_summary_json(_make_diff(_non_breaking_change()), dest)
    data = json.loads(dest.read_text())
    assert data["has_breaking_changes"] is False
