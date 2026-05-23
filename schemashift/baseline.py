"""Baseline management for SchemaShift.

Allows saving and loading a 'baseline' schema snapshot to compare future
schemas against, enabling drift detection over time.
"""

import json
import os
from typing import Optional

from schemashift.loader import load_schema_from_string
from schemashift.models import Schema

DEFAULT_BASELINE_PATH = ".schemashift_baseline.json"


def save_baseline(schema: Schema, path: str = DEFAULT_BASELINE_PATH) -> None:
    """Persist a schema as the baseline snapshot to a JSON file."""
    data = {
        "tables": {
            table_name: {
                "columns": {
                    col_name: {
                        "type": col.col_type,
                        "nullable": col.nullable,
                    }
                    for col_name, col in table.columns.items()
                }
            }
            for table_name, table in schema.tables.items()
        }
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_baseline(path: str = DEFAULT_BASELINE_PATH) -> Schema:
    """Load a previously saved baseline schema from a JSON file.

    Raises:
        FileNotFoundError: if the baseline file does not exist.
        ValueError: if the baseline file is malformed.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Baseline file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if "tables" not in data:
        raise ValueError("Malformed baseline: missing 'tables' key.")

    # Reconstruct a minimal SQL DDL string so we can reuse the existing parser.
    lines = []
    for table_name, table_data in data["tables"].items():
        col_defs = []
        for col_name, col_info in table_data.get("columns", {}).items():
            nullable_str = "" if col_info.get("nullable", True) else " NOT NULL"
            col_defs.append(f"  {col_name} {col_info['type']}{nullable_str}")
        cols_joined = ",\n".join(col_defs)
        lines.append(f"CREATE TABLE {table_name} (\n{cols_joined}\n);")

    ddl = "\n\n".join(lines)
    return load_schema_from_string(ddl)


def baseline_exists(path: str = DEFAULT_BASELINE_PATH) -> bool:
    """Return True if a baseline file exists at the given path."""
    return os.path.exists(path)
