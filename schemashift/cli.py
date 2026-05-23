"""Command-line interface for schemashift."""

import argparse
import sys

from schemashift.loader import load_schema_from_file
from schemashift.differ import diff_schemas
from schemashift.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schemashift",
        description="Detect and document breaking schema changes across database migrations.",
    )
    parser.add_argument(
        "before",
        metavar="BEFORE_SQL",
        help="Path to the SQL file representing the old schema.",
    )
    parser.add_argument(
        "after",
        metavar="AFTER_SQL",
        help="Path to the SQL file representing the new schema.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if breaking changes are detected.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the schemashift CLI.

    Returns:
        Exit code: 0 for success, 1 if breaking changes found (with --exit-code),
        2 for usage errors.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        before_schema = load_schema_from_file(args.before)
        after_schema = load_schema_from_file(args.after)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    diff = diff_schemas(before_schema, after_schema)
    print_report(diff)

    if args.exit_code and diff.has_breaking_changes:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
