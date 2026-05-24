"""Tests for schemashift.scorer."""

import pytest

from schemashift.models import SchemaChange, ChangeType, SchemaDiff
from schemashift.scorer import score_diff, DiffScore, _risk_level


def _change(change_type: ChangeType, table="users", column=None, detail=None):
    return SchemaChange(
        change_type=change_type,
        table=table,
        column=column,
        detail=detail,
    )


def _diff(*changes):
    return SchemaDiff(changes=list(changes))


def test_empty_diff_returns_zero_score():
    result = score_diff(_diff())
    assert result.total_score == 0.0
    assert result.change_count == 0
    assert result.breaking_count == 0


def test_empty_diff_risk_level_is_low():
    result = score_diff(_diff())
    assert result.risk_level == "low"


def test_single_breaking_change_counted():
    result = score_diff(_diff(_change(ChangeType.COLUMN_REMOVED, column="email")))
    assert result.breaking_count == 1


def test_non_breaking_change_not_counted_as_breaking():
    result = score_diff(_diff(_change(ChangeType.COLUMN_ADDED, column="nickname")))
    assert result.breaking_count == 0


def test_table_removed_contributes_high_score():
    result = score_diff(_diff(_change(ChangeType.TABLE_REMOVED)))
    # weight=10, severity=high => multiplier=2.0 => 20.0
    assert result.total_score == 20.0


def test_column_added_contributes_low_score():
    result = score_diff(_diff(_change(ChangeType.COLUMN_ADDED, column="bio")))
    # weight=1, severity=low => multiplier=0.5 => 0.5
    assert result.total_score == 0.5


def test_multiple_changes_accumulate_score():
    diff = _diff(
        _change(ChangeType.COLUMN_REMOVED, column="email"),
        _change(ChangeType.COLUMN_ADDED, column="bio"),
    )
    result = score_diff(diff)
    assert result.change_count == 2
    assert result.total_score > 0


def test_risk_level_critical_threshold():
    assert _risk_level(30.0) == "critical"
    assert _risk_level(50.0) == "critical"


def test_risk_level_high_threshold():
    assert _risk_level(15.0) == "high"
    assert _risk_level(29.9) == "high"


def test_risk_level_medium_threshold():
    assert _risk_level(5.0) == "medium"
    assert _risk_level(14.9) == "medium"


def test_risk_level_low_threshold():
    assert _risk_level(0.0) == "low"
    assert _risk_level(4.9) == "low"


def test_diff_score_str_contains_risk_level():
    result = score_diff(_diff(_change(ChangeType.TABLE_REMOVED)))
    text = str(result)
    assert result.risk_level in text
    assert "Score" in text


def test_returns_diff_score_instance():
    result = score_diff(_diff())
    assert isinstance(result, DiffScore)
