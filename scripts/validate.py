#!/usr/bin/env python3
"""Validate all YAML datasets against JSON schemas.

Fixed schema-path resolution: previously "dat_01_at_command".split("_")[0]
returned "dat", so no schema was ever found. Now uses first two tokens.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
    import jsonschema
    HAS_DEPS = True
except ImportError as e:
    HAS_DEPS = False
    MISSING = str(e)

DATA_DIR = Path("data")
SCHEMA_DIR = Path("schemas")
REPORT_FILE = Path("reports/VALIDATION_REPORT.md")
VALID_STATUS = {"complete", "partial", "unknown", "inferred", "blocked", "deferred"}
VALID_SOURCE_TYPE = {"primary", "secondary", "external"}


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def schema_for_datafile(data_path):
    """Resolve schemas/dat_XX.schema.yaml for data/dat_XX_something.yaml."""
    name = data_path.stem  # e.g. "dat_01_at_command"
    parts = name.split("_")  # ["dat", "01", "at", "command"]
    if len(parts) < 2:
        return None
    return SCHEMA_DIR / f"{parts[0]}_{parts[1]}.schema.yaml"


def validate_dataset(data_path, schema_path):
    errors = []
    data = load_yaml(data_path)
    schema = load_yaml(schema_path)
    if not isinstance(data, list):
        return [f"Data file is not a list"], 0

    seen_ids = set()
    for i, record in enumerate(data):
        if not isinstance(record, dict):
            errors.append(f"[L1] Record {i}: not a mapping")
            continue
        try:
            jsonschema.validate(instance=record, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"[L1] Record {i}: {e.message[:200]}")
        rid = record.get("id")
        if rid in seen_ids:
            errors.append(f"[L2] Duplicate id: {rid}")
        seen_ids.add(rid)
        st = record.get("status")
        if st and st not in VALID_STATUS:
            errors.append(f"[L2] {rid}: invalid status '{st}'")
        sst = record.get("source_type")
        if sst and sst not in VALID_SOURCE_TYPE:
            errors.append(f"[L2] {rid}: invalid source_type '{sst}'")
        models = record.get("applicable_models") or []
        if "SIM800L" not in models:
            errors.append(f"[L2] {rid}: applicable_models missing SIM800L")
    return errors, len(data)


def main():
    lines = ["# Validation Report", ""]
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append(f"Dependencies available: {HAS_DEPS}")
    if not HAS_DEPS:
        lines.append(f"Missing dependency: {MISSING}")
        lines.append("")
        lines.append("Run: pip install -r requirements.txt")
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
        print("Validation skipped: missing deps")
        return 2

    datasets = sorted(DATA_DIR.glob("dat_*.yaml"))
    total_records = 0
    total_errors = 0
    per_dataset = []

    for data_path in datasets:
        name = data_path.stem
        schema_path = schema_for_datafile(data_path)
        if schema_path is None or not schema_path.exists():
            msg = f"## {name}: SCHEMA MISSING ({schema_path})"
            lines.append(msg)
            per_dataset.append((name, 0, 0, False))
            total_errors += 1
            continue
        errs, count = validate_dataset(data_path, schema_path)
        total_records += count
        if errs:
            lines.append(f"## {name}: {len(errs)} errors ({count} records)")
            for e in errs[:20]:
                lines.append(f"  - {e}")
            total_errors += len(errs)
            per_dataset.append((name, count, len(errs), True))
        else:
            lines.append(f"## {name}: OK ({count} records)")
            per_dataset.append((name, count, 0, True))

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Dataset | Records | Errors | Schema |")
    lines.append("|---|---|---|---|")
    for (n, c, e, s) in per_dataset:
        lines.append(f"| {n} | {c} | {e} | {'yes' if s else 'NO'} |")
    lines.append("")
    lines.append(f"**Total records: {total_records}**")
    lines.append(f"**Total errors: {total_errors}**")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Validation: {total_records} records, {total_errors} errors")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())