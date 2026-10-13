# sim800l-data

Structured, source-backed datasets for the **SIM800L** module.

## Live status

See `reports/COVERAGE_MATRIX.md` and `reports/CROSS_REF_REPORT.md`.

## Layout

| Path | Purpose |
|---|---|
| `data/` | 18 YAML datasets (`dat_01` … `dat_18`) |
| `schemas/` | JSON-Schema draft-07 per dataset |
| `sources/originals/` | Immutable source PDFs |
| `sources/extracted/` | Extracted text/tables/AT-command index |
| `scripts/` | Python tooling |
| `reports/` | Reports and logs |

## Scripts

- `extract_at_commands.py` — scan AT Manual PDFs, emit `at_commands.json`.
- `add_missing_at_commands.py` — merge new commands into `dat_01`.
- `_rebuild_dat15.py` — content-filter `dat_15`.
- `fix_validation_errors.py` — apply safe defaults.
- `validate.py`, `cross_ref.py`, `coverage_report.py` — QA pass.

## Rules

1. Only SIM800L. `applicable_models` must include it.
2. Every record must carry `source`, `source_type`, `confidence`, `status`.
3. `V2.02` hardware supersedes `V1.00`.
4. No synthetic data.
5. Timestamps are UTC ISO 8601.