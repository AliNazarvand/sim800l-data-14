#!/usr/bin/env python3
"""Merge AT commands discovered in PDFs into dat_01.

Reads sources/extracted/at_commands.json, compares to data/dat_01_at_command.yaml,
and appends any missing commands as new records.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML missing")
    sys.exit(2)

EXTRACTED = Path("sources/extracted/at_commands.json")
DAT01 = Path("data/dat_01_at_command.yaml")

CATEGORY_HINTS = [
    (re.compile(r'^\+CMG|^\+CMT|^\+CMR|^\+CMG|^\+CMSS|^\+CMGF|^\+CPMS|^\+CSMS|^\+CNMI|^\+CSCA|^\+CSCS'), "SMS"),
    (re.compile(r'^\+CGATT|^\+CGDCONT|^\+CGACT|^\+CGREG|^\+CGPADDR|^\+CGCONTRDP|^\+CSTT|^\+CIICR|^\+CIFSR'), "GPRS"),
    (re.compile(r'^\+CIP|^\+CDNS'), "TCP/IP"),
    (re.compile(r'^\+HTTP'), "HTTP"),
    (re.compile(r'^\+FTP'), "FTP"),
    (re.compile(r'^\+SSL'), "SSL"),
    (re.compile(r'^\+CPIN|^\+CLCK|^\+CPWD|^\+CSIM|^\+CRSM|^\+CIMI|^\+CCID|^\+CSMINS|^\+CSPN'), "SIM"),
    (re.compile(r'^\+CAUD|^\+CRSL|^\+CLVL|^\+CMUT|^\+CSDT|^\+CTON|^\+CRTT'), "Audio"),
    (re.compile(r'^\+CFUN|^\+CSCLK|^\+CBAT|^\+CBC'), "Power"),
    (re.compile(r'^\+CREG|^\+COPS|^\+CSQ|^\+CNUM'), "Network"),
    (re.compile(r'^\+CLIP|^\+CRING|^\+CCWA|^\+CHLD|^\+CLCC|^\+ATA|^\+ATD|^\+ATH|^\+CHUP'), "Call"),
    (re.compile(r'^\+CGSN|^\+GMI|^\+GMM|^\+GMR|^\+CCID'), "General"),
]


def normalize(cmd):
    if not cmd:
        return ""
    c = str(cmd).strip().upper()
    if c.startswith("AT+"):
        c = "+" + c[3:]
    elif not c.startswith("+"):
        c = "+" + c
    return c


def infer_category(cmd):
    for pat, cat in CATEGORY_HINTS:
        if pat.search(cmd):
            return cat
    return "General"


def load_existing(path):
    if not path.exists():
        return [], set(), 0
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    cmds = set()
    max_id = 0
    for rec in data:
        n = normalize(rec.get("command") or "")
        if n:
            cmds.add(n)
        rid = rec.get("id") or ""
        m = re.match(r'dat_01_(\d+)', rid)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return data, cmds, max_id


def main():
    if not EXTRACTED.exists():
        print(f"Not found: {EXTRACTED}")
        return 1

    existing, cmds, max_id = load_existing(DAT01)
    before = len(existing)

    extracted = json.loads(EXTRACTED.read_text(encoding="utf-8"))
    all_extracted = {}
    for version, entries in extracted.items():
        for cmd, page in entries.items():
            n = normalize(cmd)
            if n and n not in all_extracted:
                all_extracted[n] = {"version": version, "page": page}

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    added = 0
    for cmd in sorted(all_extracted.keys()):
        if cmd in cmds:
            continue
        info = all_extracted[cmd]
        max_id += 1
        record = {
            "id": f"dat_01_{max_id:04d}",
            "category": infer_category(cmd),
            "command": cmd,
            "mode": "exec",
            "syntax": cmd,
            "parameters": [],
            "response_success": "OK",
            "response_error": "ERROR",
            "examples": [],
            "related_urcs": [],
            "related_states": [],
            "related_commands": [],
            "firmware_min": None,
            "firmware_max": None,
            "source": {
                "name": "SIM800 Series AT Command Manual",
                "version": info["version"],
                "date": "2013-07-23",
                "page": str(info["page"]),
                "section": None,
                "quote": None,
            },
            "source_type": "primary",
            "confidence": 0.7,
            "status": "partial",
            "conflicts": [],
            "notes": "Auto-extracted from PDF during v4 rebuild. Needs manual review.",
            "tags": ["auto-extracted"],
            "applicable_models": ["SIM800L"],
            "created_at": now,
            "updated_at": now,
        }
        existing.append(record)
        cmds.add(cmd)
        added += 1

    if added > 0:
        with open(DAT01, "w", encoding="utf-8") as f:
            yaml.safe_dump(existing, f, allow_unicode=True, sort_keys=False)

    print(f"dat_01: {before} -> {before + added} (+{added} from PDFs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())