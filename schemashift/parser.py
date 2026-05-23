"""Parse SQL CREATE TABLE statements into schema dictionaries."""

import re
from typing import Dict, Any


# Matches: CREATE TABLE [IF NOT EXISTS] table_name ( ... )
CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.+)\)\s*;?",
    re.IGNORECASE | re.DOTALL,
)

# Matches a column definition line: col_name DATA_TYPE [constraints...]
COLUMN_RE = re.compile(
    r"^\s*`?(\w+)`?\s+([A-Z]+(?:\s*\([^)]*\))?)",
    re.IGNORECASE,
)


def parse_schema(sql: str) -> Dict[str, Any]:
    """Parse one or more CREATE TABLE statements and return a schema dict.

    Returns a dict of the form::

        {
            "table_name": {
                "columns": {
                    "col_name": {"type": "VARCHAR(255)", ...}
                }
            }
        }
    """
    schema: Dict[str, Any] = {}
    for match in CREATE_TABLE_RE.finditer(sql):
        table_name = match.group(1)
        body = match.group(2)
        columns = _parse_columns(body)
        schema[table_name] = {"columns": columns}
    return schema


def _parse_columns(body: str) -> Dict[str, Any]:
    """Extract column definitions from the body of a CREATE TABLE statement."""
    columns: Dict[str, Any] = {}
    for line in body.split(","):
        line = line.strip()
        # Skip table-level constraints (PRIMARY KEY, INDEX, UNIQUE, etc.)
        if re.match(r"^(PRIMARY|UNIQUE|INDEX|KEY|CONSTRAINT|CHECK|FOREIGN)", line, re.IGNORECASE):
            continue
        col_match = COLUMN_RE.match(line)
        if col_match:
            col_name = col_match.group(1)
            col_type = col_match.group(2).upper().strip()
            nullable = "NOT NULL" not in line.upper()
            columns[col_name] = {"type": col_type, "nullable": nullable}
    return columns
