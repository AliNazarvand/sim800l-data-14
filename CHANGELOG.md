# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- All 18 JSON schemas verified on disk.
- `scripts/ocr_pdf.py` for scanned-PDF OCR.
- `scripts/coverage_report.py` for auto-generated coverage matrix.
- `scripts/_rebuild_dat15.py` with content-based filtering.
- `requirements.txt` and CI workflow.
- `README.md`, `PHASE_1_REPORT.md`, `CHANGELOG.md`.

### Changed
- `scripts/validate.py` — corrected schema path resolution (`dat_01`, not `dat`).
- `scripts/cross_ref.py` — distinguishes mismatch from invalid.
- `scripts/_rebuild_dat15.py` — filters non-power content instead of dedup.
- All timestamps in UTC ISO 8601 (InvariantCulture).

### Fixed
- Persian-calendar date leak in reports.
- `validate.py` schema-path bug (previously every schema reported missing).
- `CHANGELOG.md` bad escape (`\False` -> `$false`).