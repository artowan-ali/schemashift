"""Tests for schemashift.annotator."""

import pytest
from schemashift.models import SchemaChange, ChangeType
from schemashift.annotator import (
    annotate_change,
    annotate_all,
    AnnotatedChange,
    SEVERITY_HIGH,
    SEVERITY_MEDIUM,
    SEVERITY_LOW,
)


def _change(change_type: ChangeType, table="users", column=None, detail=None):
    return SchemaChange(
        table=table,
        column=column,
        change_type=change_type,
        detail=detail,
    )


def test_annotate_column_removed_is_high_severity():
    change = _change(ChangeType.COLUMN_REMOVED, column="email")
    result = annotate_change(change)
    assert result.severity == SEVERITY_HIGH


def test_annotate_column_added_is_low_severity():
    change = _change(ChangeType.COLUMN_ADDED, column="nickname")
    result = annotate_change(change)
    assert result.severity == SEVERITY_LOW


def test_annotate_table_removed_is_high_severity():
    change = _change(ChangeType.TABLE_REMOVED)
    result = annotate_change(change)
    assert result.severity == SEVERITY_HIGH


def test_annotate_table_added_is_low_severity():
    change = _change(ChangeType.TABLE_ADDED)
    result = annotate_change(change)
    assert result.severity == SEVERITY_LOW


def test_annotate_nullable_changed_is_medium_severity():
    change = _change(ChangeType.COLUMN_NULLABLE_CHANGED, column="bio")
    result = annotate_change(change)
    assert result.severity == SEVERITY_MEDIUM


def test_annotate_type_changed_is_high_severity():
    change = _change(ChangeType.COLUMN_TYPE_CHANGED, column="age", detail="int -> varchar")
    result = annotate_change(change)
    assert result.severity == SEVERITY_HIGH


def test_annotated_change_has_explanation():
    change = _change(ChangeType.COLUMN_REMOVED, column="email")
    result = annotate_change(change)
    assert isinstance(result.explanation, str)
    assert len(result.explanation) > 0


def test_column_removed_has_suggestion():
    change = _change(ChangeType.COLUMN_REMOVED, column="email")
    result = annotate_change(change)
    assert result.suggestion is not None


def test_column_added_has_no_suggestion():
    change = _change(ChangeType.COLUMN_ADDED, column="nickname")
    result = annotate_change(change)
    assert result.suggestion is None


def test_annotated_change_is_breaking_reflects_underlying():
    breaking = _change(ChangeType.COLUMN_REMOVED, column="id")
    non_breaking = _change(ChangeType.COLUMN_ADDED, column="nickname")
    assert annotate_change(breaking).is_breaking() is True
    assert annotate_change(non_breaking).is_breaking() is False


def test_annotate_all_returns_list_of_annotated_changes():
    changes = [
        _change(ChangeType.COLUMN_REMOVED, column="email"),
        _change(ChangeType.COLUMN_ADDED, column="phone"),
    ]
    results = annotate_all(changes)
    assert len(results) == 2
    assert all(isinstance(r, AnnotatedChange) for r in results)


def test_annotate_all_empty_list():
    assert annotate_all([]) == []


def test_str_representation_contains_severity():
    change = _change(ChangeType.TABLE_REMOVED)
    result = annotate_change(change)
    assert "HIGH" in str(result)


def test_str_representation_contains_explanation():
    change = _change(ChangeType.COLUMN_TYPE_CHANGED, column="price", detail="int -> text")
    result = annotate_change(change)
    assert "Explanation" in str(result)
