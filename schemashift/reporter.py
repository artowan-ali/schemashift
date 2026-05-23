"""Formats and outputs SchemaDiff results as human-readable reports."""

from __future__ import annotations

from typing import IO
import sys

from schemashift.models import SchemaDiff, ChangeType


_BREAKING_LABEL = "[BREAKING]"
_NON_BREAKING_LABEL = "[non-breaking]"

_ICONS = {
    ChangeType.COLUMN_REMOVED: "−",
    ChangeType.COLUMN_ADDED: "+",
    ChangeType.COLUMN_TYPE_CHANGED: "~",
    ChangeType.TABLE_REMOVED: "−",
    ChangeType.TABLE_ADDED: "+",
    ChangeType.NULLABLE_CHANGED: "~",
    ChangeType.DEFAULT_CHANGED: "~",
}


def format_report(diff: SchemaDiff, *, include_non_breaking: bool = True) -> str:
    """Return a formatted string report for *diff*.

    Args:
        diff: The diff to format.
        include_non_breaking: When *False*, only breaking changes are included.

    Returns:
        A multi-line string suitable for printing to a terminal or log.
    """
    changes = diff.changes if include_non_breaking else diff.breaking_changes

    if not changes:
        return "No schema changes detected.\n"

    lines: list[str] = []
    breaking_count = sum(1 for c in changes if c.is_breaking)
    non_breaking_count = len(changes) - breaking_count

    lines.append(f"Schema diff — {len(changes)} change(s) "
                 f"({breaking_count} breaking, {non_breaking_count} non-breaking)")
    lines.append("-" * 60)

    for change in changes:
        icon = _ICONS.get(change.change_type, "?")
        label = _BREAKING_LABEL if change.is_breaking else _NON_BREAKING_LABEL
        location = (
            f"{change.table}.{change.column}" if change.column else change.table
        )
        detail = f" ({change.detail})" if change.detail else ""
        lines.append(f"  {icon} {label} {change.change_type.value} — {location}{detail}")

    lines.append("-" * 60)
    return "\n".join(lines) + "\n"


def print_report(
    diff: SchemaDiff,
    *,
    include_non_breaking: bool = True,
    file: IO[str] | None = None,
) -> None:
    """Print a formatted report for *diff* to *file* (default: stdout)."""
    output = file or sys.stdout
    output.write(format_report(diff, include_non_breaking=include_non_breaking))
