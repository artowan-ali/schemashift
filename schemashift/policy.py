"""Policy engine for enforcing schema change rules."""

from dataclasses import dataclass, field
from typing import List, Optional
from schemashift.models import SchemaChange, ChangeType
from schemashift.annotator import AnnotatedChange


@dataclass
class PolicyRule:
    """A single policy rule that can block certain change types."""
    name: str
    blocked_change_types: List[ChangeType] = field(default_factory=list)
    blocked_tables: List[str] = field(default_factory=list)
    message: str = "Change blocked by policy"

    def violates(self, change: SchemaChange) -> bool:
        """Return True if the given change violates this rule."""
        type_blocked = (
            change.change_type in self.blocked_change_types
            if self.blocked_change_types else False
        )
        table_blocked = (
            change.table in self.blocked_tables
            if self.blocked_tables else False
        )
        if self.blocked_change_types and self.blocked_tables:
            return type_blocked and table_blocked
        return type_blocked or table_blocked


@dataclass
class PolicyViolation:
    """Represents a policy violation for a specific change."""
    rule_name: str
    change: SchemaChange
    message: str

    def __str__(self) -> str:
        return f"[{self.rule_name}] {self.message} — {self.change}"


@dataclass
class PolicyResult:
    """Result of running policy checks against a diff."""
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def __str__(self) -> str:
        if self.passed:
            return "Policy check passed: no violations."
        lines = [f"Policy check failed: {len(self.violations)} violation(s)"]
        for v in self.violations:
            lines.append(f"  - {v}")
        return "\n".join(lines)


def check_policy(
    changes: List[SchemaChange],
    rules: List[PolicyRule]
) -> PolicyResult:
    """Run all policy rules against a list of schema changes."""
    violations: List[PolicyViolation] = []
    for change in changes:
        for rule in rules:
            if rule.violates(change):
                violations.append(PolicyViolation(
                    rule_name=rule.name,
                    change=change,
                    message=rule.message
                ))
    return PolicyResult(violations=violations)
