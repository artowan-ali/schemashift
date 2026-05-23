"""Load schema definitions from SQL files or raw SQL strings."""

from pathlib import Path
from typing import Dict, Any

from schemashift.parser import parse_schema


def load_schema_from_file(path: str | Path) -> Dict[str, Any]:
    """Read a SQL file and parse its CREATE TABLE statements.

    Args:
        path: Path to a ``.sql`` file.

    Returns:
        Parsed schema dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains no recognisable CREATE TABLE statements.
    """
    sql_path = Path(path)
    if not sql_path.exists():
        raise FileNotFoundError(f"Schema file not found: {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")
    return load_schema_from_string(sql)


def load_schema_from_string(sql: str) -> Dict[str, Any]:
    """Parse CREATE TABLE statements from a raw SQL string.

    Args:
        sql: SQL text containing one or more CREATE TABLE statements.

    Returns:
        Parsed schema dictionary.

    Raises:
        ValueError: If no CREATE TABLE statements are found.
    """
    schema = parse_schema(sql)
    if not schema:
        raise ValueError("No CREATE TABLE statements found in the provided SQL.")
    return schema
