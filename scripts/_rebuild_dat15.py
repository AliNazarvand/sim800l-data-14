#!/usr/bin/env python3
"""Rebuild dat_15 by CONTENT filtering (corrected).

Fix from v3: do NOT include the `category` field in the keyword search,
because every record's category contains "Power" and would trivially match.
Also require the power keyword to appear inside `parameter` with word
boundaries. Records whose parameter looks like prose (starts with lowercase,
has no number/unit) are dropped.
"""
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("PyYAML missing")
    sys.exit(2)

DATA_FILE = Path("data/dat_15_power_management.yaml")
ARCHIVE_DIR = Path("data/_archive")

INVALID_PATTERNS = [
    re.compile(r'\.\.\.\d+\s*$'),                       # "...60"
    re.compile(r'^TABLE\s+\d', re.IGNORECASE),          # "TABLE 3:"
    re.compile(r'^Figure\s+\d', re.IGNORECASE),
    re.compile(r'^[\d\.\s\-/]+$'),                      # only numbers
    re.compile(r'^[ivxIVX]+$'),
    re.compile(r'^(page|rev|version|date)\b', re.IGNORECASE),
    re.compile(r'^(SIMCom|This document|Copyright|All rights)', re.IGNORECASE),
    re.compile(r'^[a-z]'),                              # starts lowercase = fragment
    re.compile(r'proprietary', re.IGNORECASE),
]

INVALID_CATEGORY_HINTS = {
    "audio", "keypad", "mic", "spk", "package", "safety",
    "marking", "features", "references", "smart machine",
}

SPECIFIC_KEYWORDS = [
    r'\bcurrent\b', r'\bvoltage\b', r'\bsleep\b', r'\bwake\b', r'\bdtr\b',
    r'\bpwrkey\b', r'\bcfun\b', r'\brtc\b', r'\bvbat\b', r'\bstandby\b',
    r'\bconsumption\b', r'\bcharge\b', r'\bdeep sleep\b', r'\bidle\b',
    r'\bma\b', r'\bua\b', r'\bmw\b', r'\bminimum functionality\b',
]
KEYWORD_RES = [re.compile(k, re.IGNORECASE) for k in SPECIFIC_KEYWORDS]


def is_valid_power_record(rec):
    if not isinstance(rec, dict):
        return False

    param = (rec.get("parameter") or "").strip()
    if not param or len(param) < 4:
        return False

    for pat in INVALID_PATTERNS:
        if pat.search(param):
            return False

    words = [w for w in re.split(r'\s+', param) if re.search(r'[A-Za-z]', w)]
    if len(words) < 2:
        return False

    cat = (rec.get("category") or "").strip().lower()
    if any(hint in cat for hint in INVALID_CATEGORY_HINTS):
        return False

    # IMPORTANT: check param ONLY (not category)
    if not any(r.search(param) for r in KEYWORD_RES):
        return False

    # Require either a digit or a unit token (real measurement)
    if not re.search(r'\d', param) and not re.search(r'\b(ma|ua|mw|mv|v|ms|us)\b', param, re.IGNORECASE):
        # Allow pure-name parameters like "Sleep Mode 1"
        if not re.search(r'\b(sleep|wake|dtr|pwrkey|cfun|rtc)\b', param, re.IGNORECASE):
            return False

    return True


def renumber(records):
    out = []
    for i, rec in enumerate(records, start=1):
        rec = dict(rec)
        rec["id"] = f"dat_15_{i:04d}"
        out.append(rec)
    return out


def main():
    if not DATA_FILE.exists():
        print(f"Not found: {DATA_FILE}")
        return 1
    original = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8")) or []
    before = len(original)
    filtered = [r for r in original if is_valid_power_record(r)]
    after_list = renumber(filtered)
    after = len(after_list)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    archive = ARCHIVE_DIR / f"dat_15_power_management_{stamp}.yaml"
    shutil.copy2(str(DATA_FILE), str(archive))

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(after_list, f, allow_unicode=True, sort_keys=False)

    print(f"dat_15: {before} -> {after} (archived: {archive})")
    return 0


if __name__ == "__main__":
    sys.exit(main())