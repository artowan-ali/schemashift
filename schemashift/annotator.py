"""Annotate schema changes with severity levels and human-readable explanations."""

from dataclasses import dataclass
from typing import Optional

from schemashift.models import SchemaChange, ChangeType


SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"


@dataclass
class AnnotatedChange:
    change: SchemaChange
    severity: str
    explanation: str
    suggestion: Optional[str] = None

    def is_breaking(self) -> bool:
        return self.change.is_breaking()

    def __str__(self) -> str:
        parts = [f"[{self.severity.upper()}] {self.change}"]
        parts.append(f"  Explanation: {self.explanation}")
        if self.suggestion:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)


_EXPLANATIONS = {
    ChangeType.COLUMN_REMOVED: (
        SEVERITY_HIGH,
        "Removing a column is a breaking change; existing queries referencing it will fail.",
        "Deprecate the column first, then remove it in a later migration.",
    ),
    ChangeType.COLUMN_TYPE_CHANGED: (
        SEVERITY_HIGH,
        "Changing a column type may cause data loss or application errors.",
        "Add a new column with the desired type and migrate data before removing the old one.",
    ),
    ChangeType.TABLE_REMOVED: (
        SEVERITY_HIGH,
        "Removing a table is a breaking change; all dependent queries and foreign keys will break.",
        "Ensure no application code references this table before dropping it.",
    ),
    ChangeType.COLUMN_ADDED: (
        SEVERITY_LOW,
        "Adding a nullable column is generally safe for existing queries.",
        None,
    ),
    ChangeType.TABLE_ADDED: (
        SEVERITY_LOW,
        "Adding a new table does not affect existing queries.",
        None,
    ),
    ChangeType.COLUMN_NULLABLE_CHANGED: (
        SEVERITY_MEDIUM,
        "Changing nullability can break inserts that omit the column or violate new constraints.",
        "Verify all insert paths supply a value before adding a NOT NULL constraint.",
    ),
}


def annotate_change(change: SchemaChange) -> AnnotatedChange:
    """Return an AnnotatedChange with severity and explanation for a SchemaChange."""
    severity, explanation, suggestion = _EXPLANATIONS.get(
        change.change_type,
        (SEVERITY_MEDIUM, "Unknown change type.", None),
    )
    return AnnotatedChange(
        change=change,
        severity=severity,
        explanation=explanation,
        suggestion=suggestion,
    )


def annotate_all(changes: list) -> list:
    """Annotate a list of SchemaChange objects."""
    return [annotate_change(c) for c in changes]
