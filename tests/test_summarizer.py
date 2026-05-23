"""Tests for schemashift.summarizer."""

import pytest

from schemashift.models import ChangeType, SchemaChange, SchemaDiff
from schemashift.summarizer import summarize, DiffSummary


def _make_diff(*changes: SchemaChange) -> SchemaDiff:
    return SchemaDiff(changes=list(changes))


def _change(
    change_type: ChangeType,
    table: str = "users",
    column: str | None = "id",
    breaking: bool = True,
    detail: str | None = None,
) -> SchemaChange:
    return SchemaChange(
        change_type=change_type,
        table=table,
        column=column,
        is_breaking=breaking,
        detail=detail,
    )


def test_empty_diff_returns_zero_counts():
    summary = summarize(_make_diff())
    assert summary.total_changes == 0
    assert summary.breaking_count == 0
    assert summary.non_breaking_count == 0
    assert summary.counts_by_type == {}


def test_has_breaking_changes_false_when_empty():
    summary = summarize(_make_diff())
    assert summary.has_breaking_changes is False


def test_breaking_change_counted():
    diff = _make_diff(_change(ChangeType.COLUMN_REMOVED, breaking=True))
    summary = summarize(diff)
    assert summary.breaking_count == 1
    assert summary.non_breaking_count == 0
    assert summary.has_breaking_changes is True


def test_non_breaking_change_counted():
    diff = _make_diff(_change(ChangeType.COLUMN_ADDED, breaking=False))
    summary = summarize(diff)
    assert summary.breaking_count == 0
    assert summary.non_breaking_count == 1
    assert summary.has_breaking_changes is False


def test_total_changes_matches_all_entries():
    diff = _make_diff(
        _change(ChangeType.COLUMN_REMOVED, breaking=True),
        _change(ChangeType.COLUMN_ADDED, breaking=False),
        _change(ChangeType.COLUMN_TYPE_CHANGED, breaking=True),
    )
    summary = summarize(diff)
    assert summary.total_changes == 3


def test_counts_by_type_aggregated():
    diff = _make_diff(
        _change(ChangeType.COLUMN_REMOVED, breaking=True),
        _change(ChangeType.COLUMN_REMOVED, table="orders", breaking=True),
        _change(ChangeType.COLUMN_ADDED, breaking=False),
    )
    summary = summarize(diff)
    assert summary.counts_by_type[ChangeType.COLUMN_REMOVED.value] == 2
    assert summary.counts_by_type[ChangeType.COLUMN_ADDED.value] == 1


def test_str_output_contains_counts():
    diff = _make_diff(
        _change(ChangeType.COLUMN_REMOVED, breaking=True),
        _change(ChangeType.COLUMN_ADDED, breaking=False),
    )
    text = str(summarize(diff))
    assert "Total changes" in text
    assert "Breaking" in text
    assert "Non-breaking" in text
