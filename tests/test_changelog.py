"""Tests for schemashift.changelog."""

import pytest
from schemashift.models import SchemaDiff, SchemaChange, ChangeType
from schemashift.changelog import build_changelog, ChangelogEntry


def _change(change_type: ChangeType, table="users", column=None, detail=None) -> SchemaChange:
    return SchemaChange(
        change_type=change_type,
        table=table,
        column=column,
        detail=detail,
    )


def _diff(*changes: SchemaChange) -> SchemaDiff:
    return SchemaDiff(changes=list(changes))


def test_build_changelog_returns_entry():
    diff = _diff()
    entry = build_changelog(diff)
    assert isinstance(entry, ChangelogEntry)


def test_empty_diff_zero_counts():
    diff = _diff()
    entry = build_changelog(diff)
    assert entry.breaking_count == 0
    assert entry.non_breaking_count == 0


def test_breaking_change_counted():
    diff = _diff(_change(ChangeType.COLUMN_REMOVED, column="email"))
    entry = build_changelog(diff)
    assert entry.breaking_count == 1
    assert entry.non_breaking_count == 0


def test_non_breaking_change_counted():
    diff = _diff(_change(ChangeType.COLUMN_ADDED, column="nickname"))
    entry = build_changelog(diff)
    assert entry.breaking_count == 0
    assert entry.non_breaking_count == 1


def test_version_stored_in_entry():
    diff = _diff()
    entry = build_changelog(diff, version="v2.3.0")
    assert entry.version == "v2.3.0"


def test_timestamp_stored_in_entry():
    diff = _diff()
    entry = build_changelog(diff, timestamp="2024-01-01 00:00 UTC")
    assert entry.timestamp == "2024-01-01 00:00 UTC"


def test_str_contains_version():
    diff = _diff()
    entry = build_changelog(diff, version="v1.0.0", timestamp="2024-06-01 12:00 UTC")
    output = str(entry)
    assert "v1.0.0" in output


def test_str_contains_timestamp():
    diff = _diff()
    entry = build_changelog(diff, timestamp="2024-06-01 12:00 UTC")
    output = str(entry)
    assert "2024-06-01 12:00 UTC" in output


def test_str_no_changes_message():
    diff = _diff()
    entry = build_changelog(diff, timestamp="2024-01-01 00:00 UTC")
    assert "No schema changes detected" in str(entry)


def test_str_breaking_section_present():
    diff = _diff(_change(ChangeType.COLUMN_REMOVED, column="id"))
    entry = build_changelog(diff, timestamp="2024-01-01 00:00 UTC")
    output = str(entry)
    assert "Breaking Changes" in output


def test_str_non_breaking_section_present():
    diff = _diff(_change(ChangeType.COLUMN_ADDED, column="bio"))
    entry = build_changelog(diff, timestamp="2024-01-01 00:00 UTC")
    output = str(entry)
    assert "Non-Breaking Changes" in output


def test_changes_list_populated():
    diff = _diff(
        _change(ChangeType.COLUMN_REMOVED, column="old_col"),
        _change(ChangeType.COLUMN_ADDED, column="new_col"),
    )
    entry = build_changelog(diff)
    assert len(entry.changes) == 2
