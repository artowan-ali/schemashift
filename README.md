# schemashift

> Detect and document breaking schema changes across database migrations.

---

## Installation

```bash
pip install schemashift
```

---

## Usage

Compare two migration states and generate a breaking change report:

```python
from schemashift import SchemaShift

shift = SchemaShift(
    before="migrations/v1_schema.sql",
    after="migrations/v2_schema.sql"
)

report = shift.analyze()
report.print_summary()
```

Or use the CLI directly:

```bash
schemashift compare migrations/v1_schema.sql migrations/v2_schema.sql --output report.md
```

**Example output:**

```
[BREAKING] Column 'user_id' removed from table 'orders'
[BREAKING] Column 'email' type changed: VARCHAR(100) → VARCHAR(50)
[WARNING]  Index 'idx_created_at' dropped from table 'events'
```

---

## Features

- Detects column removals, type changes, and constraint modifications
- Flags renamed tables and dropped indexes
- Outputs reports in Markdown, JSON, or plain text
- CI/CD friendly with non-zero exit codes on breaking changes

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss proposed changes.

---

## License

This project is licensed under the [MIT License](LICENSE).