"""Tests for schemashift/policy_loader.py"""

import json
import pytest
from schemashift.models import ChangeType
from schemashift.policy_loader import load_policy_from_dict, _parse_change_types


def test_load_empty_config_returns_no_rules():
    rules = load_policy_from_dict({})
    assert rules == []


def test_load_single_rule_name():
    config = {"rules": [{"name": "no_drops", "blocked_change_types": ["column_removed"]}]}
    rules = load_policy_from_dict(config)
    assert len(rules) == 1
    assert rules[0].name == "no_drops"


def test_load_rule_blocked_change_types():
    config = {"rules": [{"name": "r", "blocked_change_types": ["column_removed", "table_removed"]}]}
    rules = load_policy_from_dict(config)
    assert ChangeType.COLUMN_REMOVED in rules[0].blocked_change_types
    assert ChangeType.TABLE_REMOVED in rules[0].blocked_change_types


def test_load_rule_blocked_tables():
    config = {"rules": [{"name": "r", "blocked_tables": ["users", "payments"]}]}
    rules = load_policy_from_dict(config)
    assert "users" in rules[0].blocked_tables
    assert "payments" in rules[0].blocked_tables


def test_load_rule_custom_message():
    config = {"rules": [{"name": "r", "message": "Do not drop columns", "blocked_change_types": ["column_removed"]}]}
    rules = load_policy_from_dict(config)
    assert rules[0].message == "Do not drop columns"


def test_load_rule_default_message():
    config = {"rules": [{"name": "r", "blocked_change_types": ["column_added"]}]}
    rules = load_policy_from_dict(config)
    assert rules[0].message == "Change blocked by policy"


def test_parse_change_types_unknown_raises():
    with pytest.raises(ValueError, match="Unknown change type"):
        _parse_change_types(["not_a_real_type"])


def test_parse_change_types_case_insensitive():
    result = _parse_change_types(["COLUMN_REMOVED"])
    assert ChangeType.COLUMN_REMOVED in result


def test_load_multiple_rules():
    config = {
        "rules": [
            {"name": "r1", "blocked_change_types": ["column_removed"]},
            {"name": "r2", "blocked_tables": ["orders"]},
        ]
    }
    rules = load_policy_from_dict(config)
    assert len(rules) == 2
    assert rules[0].name == "r1"
    assert rules[1].name == "r2"
