"""Summarizer module: produce summary statistics from a SchemaDiff."""

from dataclasses import dataclass
from typing import Dict

from schemashift.models import SchemaDiff, ChangeType


@dataclass
class DiffSummary:
    """Aggregated statistics for a SchemaDiff."""

    total_changes: int
    breaking_count: int
    non_breaking_count: int
    counts_by_type: Dict[str, int]

    @property
    def has_breaking_changes(self) -> bool:
        return self.breaking_count > 0

    def __str__(self) -> str:
        lines = [
            f"Total changes : {self.total_changes}",
            f"Breaking       : {self.breaking_count}",
            f"Non-breaking   : {self.non_breaking_count}",
            "By type:",
        ]
        for change_type, count in sorted(self.counts_by_type.items()):
            lines.append(f"  {change_type:<30} {count}")
        return "\n".join(lines)


def summarize(diff: SchemaDiff) -> DiffSummary:
    """Return a DiffSummary computed from *diff*."""
    counts_by_type: Dict[str, int] = {}
    breaking_count = 0
    non_breaking_count = 0

    for change in diff.changes:
        key = change.change_type.value
        counts_by_type[key] = counts_by_type.get(key, 0) + 1

        if change.is_breaking:
            breaking_count += 1
        else:
            non_breaking_count += 1

    return DiffSummary(
        total_changes=len(diff.changes),
        breaking_count=breaking_count,
        non_breaking_count=non_breaking_count,
        counts_by_type=counts_by_type,
    )
