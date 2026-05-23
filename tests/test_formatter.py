"""Tests for schemashift.formatter module."""

import json
import pytest

from schemashift.models import ChangeType, SchemaChange, SchemaDiff
from schemashift.formatter import to_json, to_markdown, format_output


def _make_diff(
    breaking: list[SchemaChange] | None = None,
    non_breaking: list[SchemaChange] | None = None,
) -> SchemaDiff:
    return SchemaDiff(
        breaking_changes=breaking or [],
        non_breaking_changes=non_breaking or [],
    )


# --- JSON ---

def test_to_json_empty_diff():
    diff = _make_diff()
    result = json.loads(to_json(diff))
    assert result["breaking_changes"] == []
    assert result["non_breaking_changes"] == []
    assert result["summary"]["total_breaking"] == 0
    assert result["summary"]["total_non_breaking"] == 0


def test_to_json_includes_breaking_change():
    change = SchemaChange(table="users", column="email", change_type=ChangeType.COLUMN_REMOVED)
    diff = _make_diff(breaking=[change])
    result = json.loads(to_json(diff))
    assert len(result["breaking_changes"]) == 1
    row = result["breaking_changes"][0]
    assert row["table"] == "users"
    assert row["column"] == "email"
    assert row["breaking"] is True
    assert result["summary"]["total_breaking"] == 1


def test_to_json_non_breaking_change():
    change = SchemaChange(table="orders", column="note", change_type=ChangeType.COLUMN_ADDED)
    diff = _make_diff(non_breaking=[change])
    result = json.loads(to_json(diff))
    assert len(result["non_breaking_changes"]) == 1
    assert result["non_breaking_changes"][0]["breaking"] is False


def test_to_json_detail_field_present():
    change = SchemaChange(
        table="products",
        column="price",
        change_type=ChangeType.COLUMN_TYPE_CHANGED,
        detail="int -> float",
    )
    diff = _make_diff(breaking=[change])
    result = json.loads(to_json(diff))
    assert result["breaking_changes"][0]["detail"] == "int -> float"


# --- Markdown ---

def test_to_markdown_empty_diff():
    diff = _make_diff()
    result = to_markdown(diff)
    assert "No schema changes detected" in result


def test_to_markdown_contains_table_header():
    change = SchemaChange(table="users", column="id", change_type=ChangeType.COLUMN_REMOVED)
    diff = _make_diff(breaking=[change])
    result = to_markdown(diff)
    assert "| Table |" in result
    assert "| Column |" in result


def test_to_markdown_breaking_label():
    change = SchemaChange(table="users", column="id", change_type=ChangeType.COLUMN_REMOVED)
    diff = _make_diff(breaking=[change])
    result = to_markdown(diff)
    assert "💥 Breaking" in result


def test_to_markdown_non_breaking_label():
    change = SchemaChange(table="logs", column="meta", change_type=ChangeType.COLUMN_ADDED)
    diff = _make_diff(non_breaking=[change])
    result = to_markdown(diff)
    assert "✅ Non-breaking" in result


# --- format_output dispatch ---

def test_format_output_json():
    diff = _make_diff()
    result = format_output(diff, fmt="json")
    parsed = json.loads(result)
    assert "summary" in parsed


def test_format_output_markdown():
    diff = _make_diff()
    result = format_output(diff, fmt="markdown")
    assert "SchemaShift" in result


def test_format_output_invalid_raises():
    diff = _make_diff()
    with pytest.raises(ValueError, match="Unsupported format"):
        format_output(diff, fmt="csv")  # type: ignore[arg-type]
