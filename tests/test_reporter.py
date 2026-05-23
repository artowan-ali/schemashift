"""Tests for schemashift.reporter."""

from __future__ import annotations

import io

import pytest

from schemashift.models import ChangeType, SchemaChange, SchemaDiff
from schemashift.reporter import format_report, print_report


def _make_diff(*changes: SchemaChange) -> SchemaDiff:
    return SchemaDiff(changes=list(changes))


def test_no_changes_message():
    diff = _make_diff()
    report = format_report(diff)
    assert "No schema changes detected." in report


def test_breaking_change_label_present():
    change = SchemaChange(
        change_type=ChangeType.COLUMN_REMOVED,
        table="users",
        column="email",
    )
    report = format_report(_make_diff(change))
    assert "[BREAKING]" in report
    assert "users.email" in report


def test_non_breaking_change_label_present():
    change = SchemaChange(
        change_type=ChangeType.COLUMN_ADDED,
        table="orders",
        column="note",
    )
    report = format_report(_make_diff(change))
    assert "[non-breaking]" in report
    assert "orders.note" in report


def test_detail_included_when_present():
    change = SchemaChange(
        change_type=ChangeType.COLUMN_TYPE_CHANGED,
        table="products",
        column="price",
        detail="integer -> numeric",
    )
    report = format_report(_make_diff(change))
    assert "integer -> numeric" in report


def test_exclude_non_breaking():
    breaking = SchemaChange(
        change_type=ChangeType.TABLE_REMOVED, table="legacy"
    )
    non_breaking = SchemaChange(
        change_type=ChangeType.COLUMN_ADDED, table="legacy", column="new_col"
    )
    report = format_report(_make_diff(breaking, non_breaking), include_non_breaking=False)
    assert "[BREAKING]" in report
    assert "[non-breaking]" not in report


def test_summary_counts():
    breaking = SchemaChange(
        change_type=ChangeType.COLUMN_REMOVED, table="t", column="c"
    )
    non_breaking = SchemaChange(
        change_type=ChangeType.COLUMN_ADDED, table="t", column="d"
    )
    report = format_report(_make_diff(breaking, non_breaking))
    assert "2 change(s)" in report
    assert "1 breaking" in report


def test_print_report_writes_to_file():
    change = SchemaChange(
        change_type=ChangeType.NULLABLE_CHANGED,
        table="accounts",
        column="bio",
        detail="NOT NULL -> NULL",
    )
    buf = io.StringIO()
    print_report(_make_diff(change), file=buf)
    output = buf.getvalue()
    assert "accounts.bio" in output
    assert "NOT NULL -> NULL" in output
