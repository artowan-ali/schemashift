"""Snapshot module: capture and compare schema snapshots over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from schemashift.models import Schema


@dataclass
class Snapshot:
    """A timestamped record of a schema state."""

    label: str
    timestamp: str
    schema: Schema
    metadata: Dict[str, str] = field(default_factory=dict)

    def __str__(self) -> str:
        table_count = len(self.schema.tables)
        return f"Snapshot(label={self.label!r}, tables={table_count}, at={self.timestamp})"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_snapshot(schema: Schema, label: str, metadata: Optional[Dict[str, str]] = None) -> Snapshot:
    """Create a new Snapshot from a Schema."""
    return Snapshot(
        label=label,
        timestamp=_now_iso(),
        schema=schema,
        metadata=metadata or {},
    )


def snapshot_to_dict(snapshot: Snapshot) -> dict:
    """Serialize a Snapshot to a plain dictionary."""
    return {
        "label": snapshot.label,
        "timestamp": snapshot.timestamp,
        "metadata": snapshot.metadata,
        "tables": {
            table_name: {
                col_name: {
                    "type": col.col_type,
                    "nullable": col.nullable,
                }
                for col_name, col in table.columns.items()
            }
            for table_name, table in snapshot.schema.tables.items()
        },
    }


def save_snapshot(snapshot: Snapshot, path: Path) -> None:
    """Write a Snapshot to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot_to_dict(snapshot), fh, indent=2)


def load_snapshot(path: Path) -> Snapshot:
    """Load a Snapshot from a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return _snapshot_from_dict(data)


def _snapshot_from_dict(data: dict) -> Snapshot:
    from schemashift.models import Schema, Table, Column

    tables = {}
    for table_name, cols in data.get("tables", {}).items():
        columns = {
            col_name: Column(
                name=col_name,
                col_type=col_data["type"],
                nullable=col_data["nullable"],
            )
            for col_name, col_data in cols.items()
        }
        tables[table_name] = Table(name=table_name, columns=columns)

    return Snapshot(
        label=data["label"],
        timestamp=data["timestamp"],
        schema=Schema(tables=tables),
        metadata=data.get("metadata", {}),
    )
