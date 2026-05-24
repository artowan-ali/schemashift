"""Generate a human-readable changelog from a SchemaDiff."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from schemashift.models import SchemaDiff, SchemaChange, ChangeType
from schemashift.annotator import AnnotatedChange, annotate_all


@dataclass
class ChangelogEntry:
    timestamp: str
    version: Optional[str]
    breaking_count: int
    non_breaking_count: int
    changes: List[AnnotatedChange] = field(default_factory=list)

    def __str__(self) -> str:
        lines = []
        header = f"## Schema Changelog"
        if self.version:
            header += f" — {self.version}"
        header += f" ({self.timestamp})"
        lines.append(header)
        lines.append(f"Breaking changes: {self.breaking_count}  |  Non-breaking: {self.non_breaking_count}")
        lines.append("")

        if not self.changes:
            lines.append("No schema changes detected.")
            return "\n".join(lines)

        breaking = [c for c in self.changes if c.is_breaking]
        non_breaking = [c for c in self.changes if not c.is_breaking]

        if breaking:
            lines.append("### Breaking Changes")
            for ac in breaking:
                lines.append(f"  - [{ac.severity.upper()}] {ac}")
                if ac.suggestion:
                    lines.append(f"    Suggestion: {ac.suggestion}")
            lines.append("")

        if non_breaking:
            lines.append("### Non-Breaking Changes")
            for ac in non_breaking:
                lines.append(f"  - [{ac.severity.upper()}] {ac}")
            lines.append("")

        return "\n".join(lines)


def build_changelog(
    diff: SchemaDiff,
    version: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> ChangelogEntry:
    """Build a ChangelogEntry from a SchemaDiff."""
    if timestamp is None:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    annotated = annotate_all(diff)
    breaking_count = sum(1 for a in annotated if a.is_breaking)
    non_breaking_count = len(annotated) - breaking_count

    return ChangelogEntry(
        timestamp=timestamp,
        version=version,
        breaking_count=breaking_count,
        non_breaking_count=non_breaking_count,
        changes=annotated,
    )


def print_changelog(diff: SchemaDiff, version: Optional[str] = None) -> None:
    """Print a formatted changelog to stdout."""
    entry = build_changelog(diff, version=version)
    print(str(entry))
