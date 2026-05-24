"""Scores a SchemaDiff by computing a numeric risk score based on change severity."""

from dataclasses import dataclass
from typing import List

from schemashift.models import SchemaDiff, ChangeType
from schemashift.annotator import AnnotatedChange, annotate_all

# Weight assigned to each change type for risk scoring
_CHANGE_TYPE_WEIGHTS = {
    ChangeType.TABLE_REMOVED: 10,
    ChangeType.COLUMN_REMOVED: 8,
    ChangeType.COLUMN_TYPE_CHANGED: 6,
    ChangeType.COLUMN_NULLABLE_CHANGED: 4,
    ChangeType.COLUMN_ADDED: 1,
    ChangeType.TABLE_ADDED: 1,
}

_SEVERITY_MULTIPLIERS = {
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
}


@dataclass
class DiffScore:
    total_score: float
    change_count: int
    breaking_count: int
    risk_level: str

    def __str__(self) -> str:
        return (
            f"Risk Level : {self.risk_level}\n"
            f"Total Score: {self.total_score:.1f}\n"
            f"Changes    : {self.change_count} ({self.breaking_count} breaking)"
        )


def _score_annotated(annotated: AnnotatedChange) -> float:
    base = _CHANGE_TYPE_WEIGHTS.get(annotated.change.change_type, 1)
    multiplier = _SEVERITY_MULTIPLIERS.get(annotated.severity, 1.0)
    return base * multiplier


def _risk_level(score: float) -> str:
    if score >= 30:
        return "critical"
    if score >= 15:
        return "high"
    if score >= 5:
        return "medium"
    return "low"


def score_diff(diff: SchemaDiff) -> DiffScore:
    """Compute a DiffScore for the given SchemaDiff."""
    annotated_changes: List[AnnotatedChange] = annotate_all(diff)

    total = sum(_score_annotated(a) for a in annotated_changes)
    breaking = sum(1 for a in annotated_changes if a.is_breaking)

    return DiffScore(
        total_score=total,
        change_count=len(annotated_changes),
        breaking_count=breaking,
        risk_level=_risk_level(total),
    )
