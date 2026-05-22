from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ChangeType(str, Enum):
    COLUMN_ADDED = "column_added"
    COLUMN_REMOVED = "column_removed"
    COLUMN_TYPE_CHANGED = "column_type_changed"
    COLUMN_NULLABLE_CHANGED = "column_nullable_changed"
    TABLE_ADDED = "table_added"
    TABLE_REMOVED = "table_removed"
    INDEX_ADDED = "index_added"
    INDEX_REMOVED = "index_removed"


BREAKING_CHANGES = {
    ChangeType.COLUMN_REMOVED,
    ChangeType.COLUMN_TYPE_CHANGED,
    ChangeType.TABLE_REMOVED,
    ChangeType.COLUMN_NULLABLE_CHANGED,
}


@dataclass
class SchemaChange:
    change_type: ChangeType
    table: str
    column: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: str = ""

    @property
    def is_breaking(self) -> bool:
        return self.change_type in BREAKING_CHANGES

    def __str__(self) -> str:
        breaking_label = "[BREAKING] " if self.is_breaking else ""
        return f"{breaking_label}{self.change_type.value}: {self.description}"


@dataclass
class SchemaDiff:
    changes: list[SchemaChange] = field(default_factory=list)

    @property
    def breaking_changes(self) -> list[SchemaChange]:
        return [c for c in self.changes if c.is_breaking]

    @property
    def has_breaking_changes(self) -> bool:
        return len(self.breaking_changes) > 0

    def add(self, change: SchemaChange) -> None:
        self.changes.append(change)
