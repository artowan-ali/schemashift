"""Tests for schemashift.annotation_report."""

from schemashift.models import SchemaChange, ChangeType
from schemashift.annotator import annotate_change, annotate_all
from schemashift.annotation_report import format_annotation_report


def _annotated(change_type, table="orders", column=None, detail=None):
    change = SchemaChange(table=table, column=column, change_type=change_type, detail=detail)
    return annotate_change(change)


def test_empty_returns_no_changes_message():
    result = format_annotation_report([])
    assert "No schema changes" in result


def test_report_contains_severity_label():
    items = [_annotated(ChangeType.COLUMN_REMOVED, column="price")]
    result = format_annotation_report(items)
    assert "HIGH" in result


def test_report_contains_explanation():
    items = [_annotated(ChangeType.COLUMN_REMOVED, column="price")]
    result = format_annotation_report(items)
    assert "breaking" in result.lower() or "fail" in result.lower()


def test_report_contains_suggestion_when_present():
    items = [_annotated(ChangeType.COLUMN_REMOVED, column="email")]
    result = format_annotation_report(items)
    assert "Suggestion" in result or "💡" in result


def test_report_no_suggestion_for_column_added():
    items = [_annotated(ChangeType.COLUMN_ADDED, column="nickname")]
    result = format_annotation_report(items)
    assert "💡" not in result


def test_report_summary_line_present():
    items = [
        _annotated(ChangeType.COLUMN_REMOVED, column="id"),
        _annotated(ChangeType.COLUMN_ADDED, column="slug"),
    ]
    result = format_annotation_report(items)
    assert "Summary:" in result


def test_report_summary_counts_breaking_correctly():
    items = [
        _annotated(ChangeType.COLUMN_REMOVED, column="id"),
        _annotated(ChangeType.COLUMN_ADDED, column="slug"),
    ]
    result = format_annotation_report(items)
    assert "1 breaking" in result


def test_report_high_severity_appears_before_low():
    items = [
        _annotated(ChangeType.COLUMN_ADDED, column="slug"),
        _annotated(ChangeType.COLUMN_REMOVED, column="id"),
    ]
    result = format_annotation_report(items)
    high_pos = result.index("HIGH")
    low_pos = result.index("LOW")
    assert high_pos < low_pos


def test_report_header_present():
    items = [_annotated(ChangeType.TABLE_REMOVED)]
    result = format_annotation_report(items)
    assert "Annotation Report" in result


def test_multiple_changes_all_appear():
    items = annotate_all([
        SchemaChange(table="users", column="email", change_type=ChangeType.COLUMN_REMOVED),
        SchemaChange(table="products", column=None, change_type=ChangeType.TABLE_ADDED),
        SchemaChange(table="orders", column="total", change_type=ChangeType.COLUMN_TYPE_CHANGED, detail="int->text"),
    ])
    result = format_annotation_report(items)
    assert "users" in result
    assert "products" in result
    assert "orders" in result
