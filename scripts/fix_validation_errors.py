#!/usr/bin/env python3
"""Apply safe defaults to records missing required fields.

Adds applicable_models: ["SIM800L"] if absent, sets status: partial if
status is missing, ensures source_type: primary if missing. Does NOT
fabricate data for real missing values.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML missing")
    sys.exit(2)

DATA_DIR = Path("data")


def fix_record(rec, now):
    changed = False
    if "applicable_models" not in rec or not rec.get("applicable_models"):
        rec["applicable_models"] = ["SIM800L"]
        changed = True
    elif "SIM800L" not in rec["applicable_models"]:
        rec["applicable_models"] = list(rec["applicable_models"]) + ["SIM800L"]
        changed = True

    if not rec.get("status"):
        rec["status"] = "partial"
        changed = True

    if not rec.get("source_type"):
        rec["source_type"] = "primary"
        changed = True

    if not rec.get("confidence") and rec.get("confidence") != 0:
        rec["confidence"] = 0.5
        changed = True

    if not rec.get("conflicts"):
        rec["conflicts"] = []
        changed = True

    if not rec.get("created_at"):
        rec["created_at"] = now
        changed = True

    if not rec.get("updated_at"):
        rec["updated_at"] = now
        changed = True

    return changed


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total_changed = 0
    for f in sorted(DATA_DIR.glob("dat_*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or []
        n = 0
        for rec in data:
            if isinstance(rec, dict) and fix_record(rec, now):
                n += 1
        if n:
            with open(f, "w", encoding="utf-8") as fh:
                yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False)
            print(f"  {f.name}: fixed {n} records")
            total_changed += n
    print(f"Total: {total_changed} records fixed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())