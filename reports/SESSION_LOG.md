# Session Log

## Session 2026-10-13T19:48:18Z (v4 repair)

- Action: Corrective repair pass focused on producing real data, not just reports.
- Steps executed (in order, WIP=1 discipline):
  1. Copied PDFs from disk into `sources/originals/`.
  2. Extracted AT commands from all AT Command Manuals (`scripts/extract_at_commands.py`).
  3. Merged missing commands into dat_01 (`scripts/add_missing_at_commands.py`).
  4. Rebuilt dat_15 with corrected content filter (`scripts/_rebuild_dat15.py`).
  5. Applied safe defaults to fix validation errors (`scripts/fix_validation_errors.py`).
  6. Ran `validate.py` -> `cross_ref.py` -> `coverage_report.py`.
- Files touched: see terminal output.
- Handoff: run `scripts/validate.py` again after adding any new PDF.
## Session 2026-10-13T19:52:02Z (v5 cleanup)

- Removed records with TOC-only source quotes from dat_01, dat_02, dat_03.
- Removed non-timing records from dat_04.
- Removed non-power records from dat_15.
- Regenerated COVERAGE_MATRIX.md and DATA_QUALITY_REPORT.md.
- See reports/DATA_QUALITY_REPORT.md for the honest status.

## Session 2026-10-13T19:54:40Z (v6 honest cleanup)

- Removed records from dat_01, dat_02, dat_04 with unverifiable sources.
- CLEARED dat_03 and dat_15 and marked them ``blocked`` (systematic errors).
- Coverage matrix uses priority-based status (blocked > partial > complete).
- See ``reports/DATA_QUALITY_REPORT.md`` for the honest current state.

## Session 2026-10-13T19:56:08Z (v7 table-based rebuild)

- dat_01: 365 (from at_commands.json)
- dat_03: blocked (no tables)
- dat_15: blocked (no tables)

- Coverage matrix and data quality report regenerated.
