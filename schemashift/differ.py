from typing import Any

from schemashift.models import ChangeType, SchemaChange, SchemaDiff

# Schema dict format:
# {
#   "table_name": {
#     "columns": {
#       "col_name": {"type": "VARCHAR(255)", "nullable": True}
#     },
#     "indexes": ["idx_name"]
#   }
# }


def diff_schemas(old: dict[str, Any], new: dict[str, Any]) -> SchemaDiff:
    """Compare two schema dicts and return a SchemaDiff with all detected changes."""
    result = SchemaDiff()

    old_tables = set(old.keys())
    new_tables = set(new.keys())

    for table in old_tables - new_tables:
        result.add(SchemaChange(
            change_type=ChangeType.TABLE_REMOVED,
            table=table,
            description=f"Table '{table}' was removed",
        ))

    for table in new_tables - old_tables:
        result.add(SchemaChange(
            change_type=ChangeType.TABLE_ADDED,
            table=table,
            description=f"Table '{table}' was added",
        ))

    for table in old_tables & new_tables:
        _diff_table(table, old[table], new[table], result)

    return result


def _diff_table(table: str, old: dict, new: dict, result: SchemaDiff) -> None:
    old_cols = old.get("columns", {})
    new_cols = new.get("columns", {})

    for col in set(old_cols) - set(new_cols):
        result.add(SchemaChange(
            change_type=ChangeType.COLUMN_REMOVED,
            table=table,
            column=col,
            description=f"Column '{col}' removed from table '{table}'",
        ))

    for col in set(new_cols) - set(old_cols):
        result.add(SchemaChange(
            change_type=ChangeType.COLUMN_ADDED,
            table=table,
            column=col,
            description=f"Column '{col}' added to table '{table}'",
        ))

    for col in set(old_cols) & set(new_cols):
        old_def = old_cols[col]
        new_def = new_cols[col]
        if old_def.get("type") != new_def.get("type"):
            result.add(SchemaChange(
                change_type=ChangeType.COLUMN_TYPE_CHANGED,
                table=table,
                column=col,
                old_value=old_def.get("type"),
                new_value=new_def.get("type"),
                description=f"Column '{col}' type changed from '{old_def.get('type')}' to '{new_def.get('type')}' in table '{table}'",
            ))
        if old_def.get("nullable") != new_def.get("nullable"):
            result.add(SchemaChange(
                change_type=ChangeType.COLUMN_NULLABLE_CHANGED,
                table=table,
                column=col,
                old_value=str(old_def.get("nullable")),
                new_value=str(new_def.get("nullable")),
                description=f"Column '{col}' nullable changed from {old_def.get('nullable')} to {new_def.get('nullable')} in table '{table}'",
            ))

    old_indexes = set(old.get("indexes", []))
    new_indexes = set(new.get("indexes", []))
    for idx in old_indexes - new_indexes:
        result.add(SchemaChange(change_type=ChangeType.INDEX_REMOVED, table=table, description=f"Index '{idx}' removed from table '{table}'"))
    for idx in new_indexes - old_indexes:
        result.add(SchemaChange(change_type=ChangeType.INDEX_ADDED, table=table, description=f"Index '{idx}' added to table '{table}'"))
