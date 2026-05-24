"""Tests for schemashift/comparator.py"""

import pytest
from schemashift.models import SchemaChange, ChangeType, SchemaDiff
from schemashift.comparator import compare_diffs, ComparisonResult


def _change(change_type, table="users", column=None, detail=None):
    return SchemaChange(change_type=change_type, table=table, column=column, detail=detail)


def _diff(*changes):
    return SchemaDiff(changes=list(changes))


def test_empty_diffs_return_empty_result():
    result = compare_diffs(_diff(), _diff())
    assert isinstance(result, ComparisonResult)
    assert result.resolved == []
    assert result.introduced == []
    assert result.persisted == []


def test_new_breaking_change_is_introduced():
    before = _diff()
    after = _diff(_change(ChangeType.COLUMN_REMOVED, column="email"))
    result = compare_diffs(before, after)
    assert len(result.introduced) == 1
    assert result.introduced[0].change.column == "email"


def test_resolved_change_not_in_after():
    change = _change(ChangeType.COLUMN_REMOVED, column="email")
    before = _diff(change)
    after = _diff()
    result = compare_diffs(before, after)
    assert len(result.resolved) == 1
    assert result.resolved[0].change.column == "email"


def test_persisted_change_present_in_both():
    change = _change(ChangeType.COLUMN_TYPE_CHANGED, column="age", detail="int -> text")
    before = _diff(change)
    after = _diff(change)
    result = compare_diffs(before, after)
    assert len(result.persisted) == 1
    assert result.introduced == []
    assert result.resolved == []


def test_has_regressions_true_when_breaking_introduced():
    after = _diff(_change(ChangeType.COLUMN_REMOVED, column="id"))
    result = compare_diffs(_diff(), after)
    assert result.has_regressions is True


def test_has_regressions_false_when_no_breaking_introduced():
    after = _diff(_change(ChangeType.COLUMN_ADDED, column="nickname"))
    result = compare_diffs(_diff(), after)
    assert result.has_regressions is False


def test_has_improvements_true_when_breaking_resolved():
    change = _change(ChangeType.COLUMN_REMOVED, column="token")
    result = compare_diffs(_diff(change), _diff())
    assert result.has_improvements is True


def test_has_improvements_false_when_nothing_resolved():
    result = compare_diffs(_diff(), _diff())
    assert result.has_improvements is False


def test_str_output_contains_counts():
    change = _change(ChangeType.COLUMN_REMOVED, column="legacy")
    result = compare_diffs(_diff(change), _diff())
    output = str(result)
    assert "Resolved" in output
    assert "Introduced" in output
    assert "Persisted" in output


def test_multiple_changes_classified_correctly():
    shared = _change(ChangeType.COLUMN_TYPE_CHANGED, column="score", detail="int -> float")
    old_only = _change(ChangeType.COLUMN_REMOVED, column="old_col")
    new_only = _change(ChangeType.TABLE_REMOVED, table="archive")
    before = _diff(shared, old_only)
    after = _diff(shared, new_only)
    result = compare_diffs(before, after)
    assert len(result.persisted) == 1
    assert len(result.resolved) == 1
    assert len(result.introduced) == 1
