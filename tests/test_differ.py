import pytest
from schemashift.differ import diff_schemas
from schemashift.models import ChangeType


BASE_SCHEMA = {
    "users": {
        "columns": {
            "id": {"type": "INTEGER", "nullable": False},
            "email": {"type": "VARCHAR(255)", "nullable": False},
            "name": {"type": "VARCHAR(100)", "nullable": True},
        },
        "indexes": ["idx_users_email"],
    }
}


def test_no_changes():
    diff = diff_schemas(BASE_SCHEMA, BASE_SCHEMA)
    assert len(diff.changes) == 0
    assert not diff.has_breaking_changes


def test_column_removed_is_breaking():
    new_schema = {
        "users": {
            "columns": {
                "id": {"type": "INTEGER", "nullable": False},
                "email": {"type": "VARCHAR(255)", "nullable": False},
            },
            "indexes": ["idx_users_email"],
        }
    }
    diff = diff_schemas(BASE_SCHEMA, new_schema)
    assert diff.has_breaking_changes
    removed = [c for c in diff.changes if c.change_type == ChangeType.COLUMN_REMOVED]
    assert len(removed) == 1
    assert removed[0].column == "name"
    assert removed[0].is_breaking


def test_column_added_is_not_breaking():
    new_schema = {
        "users": {
            "columns": {
                **BASE_SCHEMA["users"]["columns"],
                "phone": {"type": "VARCHAR(20)", "nullable": True},
            },
            "indexes": ["idx_users_email"],
        }
    }
    diff = diff_schemas(BASE_SCHEMA, new_schema)
    added = [c for c in diff.changes if c.change_type == ChangeType.COLUMN_ADDED]
    assert len(added) == 1
    assert not added[0].is_breaking
    assert not diff.has_breaking_changes


def test_column_type_change_is_breaking():
    new_schema = {
        "users": {
            "columns": {
                "id": {"type": "INTEGER", "nullable": False},
                "email": {"type": "TEXT", "nullable": False},
                "name": {"type": "VARCHAR(100)", "nullable": True},
            },
            "indexes": ["idx_users_email"],
        }
    }
    diff = diff_schemas(BASE_SCHEMA, new_schema)
    type_changes = [c for c in diff.changes if c.change_type == ChangeType.COLUMN_TYPE_CHANGED]
    assert len(type_changes) == 1
    assert type_changes[0].old_value == "VARCHAR(255)"
    assert type_changes[0].new_value == "TEXT"
    assert type_changes[0].is_breaking


def test_table_removed_is_breaking():
    diff = diff_schemas(BASE_SCHEMA, {})
    assert diff.has_breaking_changes
    removed = [c for c in diff.changes if c.change_type == ChangeType.TABLE_REMOVED]
    assert len(removed) == 1


def test_table_added_is_not_breaking():
    new_schema = {
        **BASE_SCHEMA,
        "orders": {
            "columns": {"id": {"type": "INTEGER", "nullable": False}},
            "indexes": [],
        },
    }
    diff = diff_schemas(BASE_SCHEMA, new_schema)
    added = [c for c in diff.changes if c.change_type == ChangeType.TABLE_ADDED]
    assert len(added) == 1
    assert not added[0].is_breaking


def test_nullable_change_is_breaking():
    new_schema = {
        "users": {
            "columns": {
                "id": {"type": "INTEGER", "nullable": False},
                "email": {"type": "VARCHAR(255)", "nullable": True},
                "name": {"type": "VARCHAR(100)", "nullable": True},
            },
            "indexes": ["idx_users_email"],
        }
    }
    diff = diff_schemas(BASE_SCHEMA, new_schema)
    nullable_changes = [c for c in diff.changes if c.change_type == ChangeType.COLUMN_NULLABLE_CHANGED]
    assert len(nullable_changes) == 1
    assert nullable_changes[0].is_breaking
