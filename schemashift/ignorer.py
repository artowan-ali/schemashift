"""Support for ignore rules that suppress specific schema changes from diffs."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from schemashift.models import SchemaChange, ChangeType


@dataclass
class IgnoreRule:
    """A single ignore rule matching changes by table, column, and/or change type."""

    table: Optional[str] = None
    column: Optional[str] = None
    change_type: Optional[str] = None

    def matches(self, change: SchemaChange) -> bool:
        """Return True if this rule applies to the given change."""
        if self.table is not None and self.table != change.table:
            return False
        if self.column is not None and self.column != change.column:
            return False
        if self.change_type is not None:
            try:
                ct = ChangeType[self.change_type.upper()]
            except KeyError:
                return False
            if ct != change.change_type:
                return False
        return True


@dataclass
class IgnoreList:
    """Collection of ignore rules."""

    rules: List[IgnoreRule] = field(default_factory=list)

    def is_ignored(self, change: SchemaChange) -> bool:
        """Return True if any rule matches the given change."""
        return any(rule.matches(change) for rule in self.rules)

    def filter(self, changes: List[SchemaChange]) -> List[SchemaChange]:
        """Return only the changes that are not suppressed by any rule."""
        return [c for c in changes if not self.is_ignored(c)]


def load_ignore_file(path: str | Path) -> IgnoreList:
    """Load an ignore list from a JSON file.

    The file should contain a top-level ``"ignore"`` array, e.g.::

        {"ignore": [{"table": "audit_log", "change_type": "column_added"}]}
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Ignore file not found: {path}")
    data = json.loads(p.read_text(encoding="utf-8"))
    rules = [
        IgnoreRule(
            table=entry.get("table"),
            column=entry.get("column"),
            change_type=entry.get("change_type"),
        )
        for entry in data.get("ignore", [])
    ]
    return IgnoreList(rules=rules)
