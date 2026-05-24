"""comparator.py — Compare two SchemaDiff results to detect regressions or improvements."""

from dataclasses import dataclass, field
from typing import List
from schemashift.models import SchemaChange, SchemaDiff
from schemashift.annotator import AnnotatedChange, annotate_all


@dataclass
class ComparisonResult:
    """Result of comparing two diffs (e.g., baseline diff vs current diff)."""
    resolved: List[AnnotatedChange] = field(default_factory=list)
    introduced: List[AnnotatedChange] = field(default_factory=list)
    persisted: List[AnnotatedChange] = field(default_factory=list)

    @property
    def has_regressions(self) -> bool:
        """True if new breaking changes were introduced."""
        return any(c.is_breaking for c in self.introduced)

    @property
    def has_improvements(self) -> bool:
        """True if previously present breaking changes were resolved."""
        return any(c.is_breaking for c in self.resolved)

    def __str__(self) -> str:
        lines = []
        lines.append(f"Resolved:    {len(self.resolved)}")
        lines.append(f"Introduced:  {len(self.introduced)}")
        lines.append(f"Persisted:   {len(self.persisted)}")
        if self.has_regressions:
            lines.append("⚠ Regressions detected.")
        if self.has_improvements:
            lines.append("✓ Improvements detected.")
        return "\n".join(lines)


def _change_key(change: SchemaChange) -> tuple:
    """Unique key identifying a schema change."""
    return (change.change_type, change.table, change.column, change.detail)


def compare_diffs(before: SchemaDiff, after: SchemaDiff) -> ComparisonResult:
    """Compare two SchemaDiff objects and classify changes as resolved, introduced, or persisted.

    Args:
        before: The earlier/baseline diff.
        after: The current/new diff.

    Returns:
        A ComparisonResult summarising what changed between the two diffs.
    """
    before_annotated = {_change_key(a.change): a for a in annotate_all(before)}
    after_annotated = {_change_key(a.change): a for a in annotate_all(after)}

    before_keys = set(before_annotated.keys())
    after_keys = set(after_annotated.keys())

    resolved = [before_annotated[k] for k in before_keys - after_keys]
    introduced = [after_annotated[k] for k in after_keys - before_keys]
    persisted = [after_annotated[k] for k in before_keys & after_keys]

    return ComparisonResult(
        resolved=resolved,
        introduced=introduced,
        persisted=persisted,
    )
