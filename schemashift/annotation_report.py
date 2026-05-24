"""Render annotated changes into a human-readable report."""

from typing import List
from schemashift.annotator import AnnotatedChange, SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW

_SEVERITY_ORDER = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 1, SEVERITY_LOW: 2}

_SEVERITY_ICONS = {
    SEVERITY_HIGH: "🔴",
    SEVERITY_MEDIUM: "🟡",
    SEVERITY_LOW: "🟢",
}


def _sort_by_severity(annotated: List[AnnotatedChange]) -> List[AnnotatedChange]:
    return sorted(annotated, key=lambda a: _SEVERITY_ORDER.get(a.severity, 99))


def format_annotation_report(annotated: List[AnnotatedChange]) -> str:
    """Return a formatted string report of annotated schema changes."""
    if not annotated:
        return "No schema changes detected."

    sorted_changes = _sort_by_severity(annotated)
    lines = ["Schema Change Annotation Report", "=" * 34, ""]

    for item in sorted_changes:
        icon = _SEVERITY_ICONS.get(item.severity, "⚪")
        lines.append(f"{icon} [{item.severity.upper()}] {item.change}")
        lines.append(f"   {item.explanation}")
        if item.suggestion:
            lines.append(f"   💡 {item.suggestion}")
        lines.append("")

    breaking = sum(1 for a in annotated if a.is_breaking())
    total = len(annotated)
    lines.append(f"Summary: {breaking} breaking / {total} total change(s)")
    return "\n".join(lines)


def print_annotation_report(annotated: List[AnnotatedChange]) -> None:
    """Print the annotation report to stdout."""
    print(format_annotation_report(annotated))
