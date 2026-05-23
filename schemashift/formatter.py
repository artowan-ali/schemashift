"""Formatter module for exporting schema diffs to structured formats (JSON, Markdown)."""

from __future__ import annotations

import json
from typing import Literal

from schemashift.models import SchemaDiff, SchemaChange


OutputFormat = Literal["json", "markdown"]


def _change_to_dict(change: SchemaChange) -> dict:
    """Serialize a SchemaChange to a plain dictionary."""
    return {
        "table": change.table,
        "column": change.column,
        "change_type": change.change_type.value,
        "breaking": change.is_breaking(),
        "detail": change.detail,
    }


def to_json(diff: SchemaDiff, indent: int = 2) -> str:
    """Serialize a SchemaDiff to a JSON string."""
    payload = {
        "breaking_changes": [_change_to_dict(c) for c in diff.breaking_changes],
        "non_breaking_changes": [_change_to_dict(c) for c in diff.non_breaking_changes],
        "summary": {
            "total_breaking": len(diff.breaking_changes),
            "total_non_breaking": len(diff.non_breaking_changes),
        },
    }
    return json.dumps(payload, indent=indent)


def _change_to_md_row(change: SchemaChange) -> str:
    """Format a SchemaChange as a Markdown table row."""
    label = "💥 Breaking" if change.is_breaking() else "✅ Non-breaking"
    col = change.column or "—"
    detail = change.detail or "—"
    return f"| {change.table} | {col} | {change.change_type.value} | {label} | {detail} |"


def to_markdown(diff: SchemaDiff) -> str:
    """Serialize a SchemaDiff to a Markdown report string."""
    lines: list[str] = []
    lines.append("# SchemaShift — Migration Report\n")

    total = len(diff.breaking_changes) + len(diff.non_breaking_changes)
    if total == 0:
        lines.append("_No schema changes detected._")
        return "\n".join(lines)

    lines.append(
        f"**{len(diff.breaking_changes)} breaking** / "
        f"**{len(diff.non_breaking_changes)} non-breaking** change(s) detected.\n"
    )
    lines.append("| Table | Column | Change | Severity | Detail |")
    lines.append("|-------|--------|--------|----------|--------|")

    for change in diff.breaking_changes + diff.non_breaking_changes:
        lines.append(_change_to_md_row(change))

    return "\n".join(lines)


def format_output(diff: SchemaDiff, fmt: OutputFormat = "markdown") -> str:
    """Dispatch formatting based on the requested output format."""
    if fmt == "json":
        return to_json(diff)
    if fmt == "markdown":
        return to_markdown(diff)
    raise ValueError(f"Unsupported format: {fmt!r}")
