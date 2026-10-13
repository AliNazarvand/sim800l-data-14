# Decisions Log

Generated: 2026-10-13T19:39:08Z

## D001 — Only SIM800L
- Decision: Every record's `applicable_models` must contain `SIM800L`.
- Rationale: Prompt R1.

## D002 — Source precedence
- Decision: `V2.02` > `V1.00` hardware; primary > secondary > external.
- Rationale: Prompt R7.

## D003 — blocked, not partial
- Decision: Missing source => `blocked`. Insufficient coverage with source => `partial`.
- Rationale: Prompt R11, R12.

## D004 — No synthetic
- Decision: No `status: synthetic` records.
- Rationale: Prompt R6.

## D005 — UTC ISO 8601 timestamps
- Decision: All timestamps UTC ISO 8601 with InvariantCulture.
- Rationale: Prompt R19.

## D006 — Fix validate.py schema-path bug
- Problem: `"dat_01_at_command".split("_")[0]` returned `"dat"`, so all 18 schemas were reported missing.
- Fix: `"_".join(name.split("_")[:2])` → `"dat_01"`.
- Date: 2026-10-13T19:39:08Z

## D007 — dat_15 rebuild by content filtering
- Problem: naive dedup produced 351 → 351 (no change) because every parameter was unique.
- Fix: drop records with page-ref suffixes, TOC markers, numeric-only parameters, unrelated categories, or no power keyword.
- Date: 2026-10-13T19:39:08Z

## D008 — Reuse discovered resources
- Decision: PDFs found by disk search are copied into `sources/originals/`.
- Rationale: Prompt "search entire disk before declaring blocked".
- Date: 2026-10-13T19:39:08Z

## D009 — Keep PowerShell window open
- Decision: `Wait-ForUserExit` runs unconditionally, with three fallbacks (Read-Host, Console.ReadLine, Start-Sleep).
- Date: 2026-10-13T19:39:08Z