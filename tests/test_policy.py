"""Tests for schemashift/policy.py"""

import pytest
from schemashift.models import SchemaChange, ChangeType
from schemashift.policy import PolicyRule, PolicyViolation, PolicyResult, check_policy


def _change(
    change_type=ChangeType.COLUMN_REMOVED,
    table="users",
    column="email",
    detail=None
) -> SchemaChange:
    return SchemaChange(change_type=change_type, table=table, column=column, detail=detail)


def test_policy_rule_violates_by_type():
    rule = PolicyRule(name="no_removals", blocked_change_types=[ChangeType.COLUMN_REMOVED])
    assert rule.violates(_change(change_type=ChangeType.COLUMN_REMOVED))
    assert not rule.violates(_change(change_type=ChangeType.COLUMN_ADDED))


def test_policy_rule_violates_by_table():
    rule = PolicyRule(name="protect_users", blocked_tables=["users"])
    assert rule.violates(_change(table="users"))
    assert not rule.violates(_change(table="orders"))


def test_policy_rule_violates_both_required_when_both_set():
    rule = PolicyRule(
        name="no_type_change_on_users",
        blocked_change_types=[ChangeType.COLUMN_TYPE_CHANGED],
        blocked_tables=["users"]
    )
    assert rule.violates(_change(change_type=ChangeType.COLUMN_TYPE_CHANGED, table="users"))
    assert not rule.violates(_change(change_type=ChangeType.COLUMN_TYPE_CHANGED, table="orders"))
    assert not rule.violates(_change(change_type=ChangeType.COLUMN_REMOVED, table="users"))


def test_check_policy_no_violations():
    rules = [PolicyRule(name="r", blocked_change_types=[ChangeType.TABLE_REMOVED])]
    changes = [_change(change_type=ChangeType.COLUMN_ADDED)]
    result = check_policy(changes, rules)
    assert result.passed
    assert result.violations == []


def test_check_policy_with_violation():
    rules = [PolicyRule(name="no_col_remove", blocked_change_types=[ChangeType.COLUMN_REMOVED])]
    changes = [_change(change_type=ChangeType.COLUMN_REMOVED)]
    result = check_policy(changes, rules)
    assert not result.passed
    assert len(result.violations) == 1
    assert result.violations[0].rule_name == "no_col_remove"


def test_check_policy_multiple_violations():
    rules = [PolicyRule(name="strict", blocked_change_types=[ChangeType.COLUMN_REMOVED, ChangeType.TABLE_REMOVED])]
    changes = [
        _change(change_type=ChangeType.COLUMN_REMOVED),
        _change(change_type=ChangeType.TABLE_REMOVED, column=None),
    ]
    result = check_policy(changes, rules)
    assert len(result.violations) == 2


def test_policy_result_str_passed():
    result = PolicyResult(violations=[])
    assert "passed" in str(result)


def test_policy_result_str_failed():
    change = _change()
    v = PolicyViolation(rule_name="r", change=change, message="blocked")
    result = PolicyResult(violations=[v])
    assert "failed" in str(result)
    assert "r" in str(result)


def test_policy_violation_str():
    change = _change()
    v = PolicyViolation(rule_name="myrule", change=change, message="Not allowed")
    s = str(v)
    assert "myrule" in s
    assert "Not allowed" in s
