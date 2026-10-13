# Data Quality Report (v7)

Generated: 2026-10-13T19:56:08Z

## What v7 changed

- `dat_01`: 365 (from at_commands.json)
- `dat_03`: blocked (no tables)
- `dat_15`: blocked (no tables)

## Method

v7 rebuilds datasets from **existing extracted CSV tables** in
`sources/extracted/tables/` and from `sources/extracted/at_commands.json`.
It does not fabricate. If a table is not found, the dataset is blocked.

## Datasets still requiring manual work

- `dat_04` — timing tables are scattered; needs page-by-page review.
- `dat_05`, `dat_06` — derived; need human semantic construction.
- `dat_07` — pin tables partially extracted; needs manual merge.
- `dat_08` — blocked: no Firmware Release Notes.
- `dat_09`..`dat_14`, `dat_16`..`dat_18` — depend on missing sources.
