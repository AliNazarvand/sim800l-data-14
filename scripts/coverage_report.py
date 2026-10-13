#!/usr/bin/env python3
"""Generate COVERAGE_MATRIX.md from current data files."""
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("PyYAML missing")
    sys.exit(2)

DATA_DIR = Path("data")
REPORT_FILE = Path("reports/COVERAGE_MATRIX.md")
EXPECTED = {
    "dat_01": "AT Command",
    "dat_02": "URC",
    "dat_03": "Error Code",
    "dat_04": "Timing",
    "dat_05": "State Machine",
    "dat_06": "Init Sequence",
    "dat_07": "Hardware",
    "dat_08": "Firmware",
    "dat_09": "SMS",
    "dat_10": "GPRS/Data",
    "dat_11": "HTTP/FTP/SSL",
    "dat_12": "Audio",
    "dat_13": "SIM Mgmt",
    "dat_14": "Operator/APN",
    "dat_15": "Power Mgmt",
    "dat_16": "Board/EVB",
    "dat_17": "Cert/Key Store",
    "dat_18": "Certification",
}
STATUSES = ["complete", "partial", "blocked", "deferred", "unknown", "inferred"]


def summarize(records):
    """Determine dominant status across records."""
    if not records:
        return "blocked", 0
    counts = {}
    for r in records:
        st = (r.get("status") or "unknown").lower()
        counts[st] = counts.get(st, 0) + 1
    if "complete" in counts and counts["complete"] == len(records):
        return "complete", len(records)
    for s in ["partial", "inferred", "unknown", "deferred", "blocked"]:
        if s in counts:
            return s, len(records)
    return "unknown", len(records)


def main():
    lines = ["# Coverage Matrix", ""]
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")
    lines.append("| Dataset | Name | Records | Status |")
    lines.append("|---|---|---|---|")
    for key in sorted(EXPECTED.keys()):
        found = None
        for f in DATA_DIR.glob(f"{key}_*.yaml"):
            found = f
            break
        if not found:
            lines.append(f"| {key} | {EXPECTED[key]} | 0 | missing |")
            continue
        try:
            data = yaml.safe_load(found.read_text(encoding="utf-8")) or []
        except Exception:
            data = []
        status, count = summarize(data)
        lines.append(f"| {key} | {EXPECTED[key]} | {count} | {status} |")
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print("Coverage matrix regenerated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())