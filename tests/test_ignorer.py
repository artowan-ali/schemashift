"""Tests for schemashift.ignorer."""

import json
import pytest
from pathlib import Path

from schemashift.models import SchemaChange, ChangeType
from schemashift.ignorer import IgnoreRule, IgnoreList, load_ignore_file


def _change(
    table="users",
    column="email",
    change_type=ChangeType.COLUMN_REMOVED,
    detail=None,
) -> SchemaChange:
    return SchemaChange(
        table=table,
        column=column,
        change_type=change_type,
        detail=detail,
    )


# ---------------------------------------------------------------------------
# IgnoreRule.matches
# ---------------------------------------------------------------------------

def test_rule_matches_by_table_only():
    rule = IgnoreRule(table="users")
    assert rule.matches(_change(table="users"))
    assert not rule.matches(_change(table="orders"))


def test_rule_matches_by_column_only():
    rule = IgnoreRule(column="email")
    assert rule.matches(_change(column="email"))
    assert not rule.matches(_change(column="name"))


def test_rule_matches_by_change_type_only():
    rule = IgnoreRule(change_type="column_removed")
    assert rule.matches(_change(change_type=ChangeType.COLUMN_REMOVED))
    assert not rule.matches(_change(change_type=ChangeType.COLUMN_ADDED))


def test_rule_matches_all_fields():
    rule = IgnoreRule(table="users", column="email", change_type="column_removed")
    assert rule.matches(_change(table="users", column="email", change_type=ChangeType.COLUMN_REMOVED))
    assert not rule.matches(_change(table="orders", column="email", change_type=ChangeType.COLUMN_REMOVED))


def test_rule_unknown_change_type_does_not_match():
    rule = IgnoreRule(change_type="nonexistent_type")
    assert not rule.matches(_change())


def test_empty_rule_matches_everything():
    rule = IgnoreRule()
    assert rule.matches(_change())


# ---------------------------------------------------------------------------
# IgnoreList
# ---------------------------------------------------------------------------

def test_ignore_list_empty_suppresses_nothing():
    il = IgnoreList()
    changes = [_change(), _change(table="orders")]
    assert il.filter(changes) == changes


def test_ignore_list_suppresses_matching_change():
    il = IgnoreList(rules=[IgnoreRule(table="users")])
    changes = [_change(table="users"), _change(table="orders")]
    result = il.filter(changes)
    assert len(result) == 1
    assert result[0].table == "orders"


def test_is_ignored_true_when_matched():
    il = IgnoreList(rules=[IgnoreRule(column="email")])
    assert il.is_ignored(_change(column="email"))


def test_is_ignored_false_when_no_match():
    il = IgnoreList(rules=[IgnoreRule(column="email")])
    assert not il.is_ignored(_change(column="name"))


# ---------------------------------------------------------------------------
# load_ignore_file
# ---------------------------------------------------------------------------

def test_load_ignore_file_parses_rules(tmp_path):
    data = {"ignore": [{"table": "audit_log", "change_type": "column_added"}]}
    p = tmp_path / ".schemaignore"
    p.write_text(json.dumps(data), encoding="utf-8")
    il = load_ignore_file(p)
    assert len(il.rules) == 1
    assert il.rules[0].table == "audit_log"
    assert il.rules[0].change_type == "column_added"


def test_load_ignore_file_empty_ignore_key(tmp_path):
    p = tmp_path / ".schemaignore"
    p.write_text(json.dumps({"ignore": []}), encoding="utf-8")
    il = load_ignore_file(p)
    assert il.rules == []


def test_load_ignore_file_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_ignore_file(tmp_path / "nonexistent.json")
