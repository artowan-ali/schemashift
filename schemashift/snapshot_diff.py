"""Utilities for diffing two Snapshots and producing a labelled report."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from schemashift.models import SchemaDiff
from schemashift.differ import diff_schemas
from schemashift.snapshot import Snapshot


@dataclass
class SnapshotDiff:
    """Result of comparing two snapshots."""

    before_label: str
    after_label: str
    before_timestamp: str
    after_timestamp: str
    diff: SchemaDiff

    @property
    def has_breaking_changes(self) -> bool:
        return any(c.is_breaking for c in self.diff.changes)

    @property
    def change_count(self) -> int:
        return len(self.diff.changes)

    def __str__(self) -> str:
        return (
            f"SnapshotDiff({self.before_label!r} -> {self.after_label!r}, "
            f"changes={self.change_count}, breaking={self.has_breaking_changes})"
        )


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiff:
    """Compare two Snapshots and return a SnapshotDiff."""
    schema_diff = diff_schemas(before.schema, after.schema)
    return SnapshotDiff(
        before_label=before.label,
        after_label=after.label,
        before_timestamp=before.timestamp,
        after_timestamp=after.timestamp,
        diff=schema_diff,
    )


def snapshot_diff_to_dict(sd: SnapshotDiff) -> dict:
    """Serialize a SnapshotDiff to a plain dictionary."""
    return {
        "before": {"label": sd.before_label, "timestamp": sd.before_timestamp},
        "after": {"label": sd.after_label, "timestamp": sd.after_timestamp},
        "has_breaking_changes": sd.has_breaking_changes,
        "change_count": sd.change_count,
        "changes": [
            {
                "change_type": c.change_type.value,
                "table": c.table,
                "column": c.column,
                "detail": c.detail,
                "is_breaking": c.is_breaking,
            }
            for c in sd.diff.changes
        ],
    }
