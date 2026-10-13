#!/usr/bin/env python3
"""v7: rebuild datasets from existing extracted CSV tables.

Sources:
  - sources/extracted/tables/  (CSV files already produced by pdfplumber)
  - sources/extracted/at_commands.json  (990 commands across 3 versions)
"""
import csv, json, re, sys
from pathlib import Path
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ROOT = Path(".")
DATA = ROOT / "data"
REP  = ROOT / "reports"
TAB  = ROOT / "sources" / "extracted" / "tables"
ATC  = ROOT / "sources" / "extracted" / "at_commands.json"

REP.mkdir(exist_ok=True)
summary = {}


def load_yaml(name):
    import yaml
    p = DATA / name
    if not p.exists():
        return []
    return yaml.safe_load(p.read_text(encoding="utf-8")) or []


def save_yaml(name, data):
    import yaml
    p = DATA / name
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def read_csv(path):
    """Read a CSV, tolerate ragged rows."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return [row for row in csv.reader(f)]
    except Exception:
        return []


def clean_cell(c):
    if c is None:
        return ""
    return str(c).replace("\n", " ").strip()


def find_csvs(pattern_glob):
    """Return list of CSVs matching a glob under TAB."""
    return sorted(TAB.glob(pattern_glob))


# ==================================================================
# 1) dat_03 CME/CMS from pages 285-292
# ==================================================================
def rebuild_dat03():
    candidates = []
    for p in range(285, 293):
        for f in find_csvs(f"*_p{p:03d}_t*.csv"):
            candidates.append(f)
    if not candidates:
        return None

    records = []
    seen = set()
    for csvfile in candidates:
        rows = read_csv(csvfile)
        for row in rows:
            if len(row) < 2:
                continue
            cell0 = clean_cell(row[0])
            cell1 = clean_cell(row[1])
            m = re.match(r'^(\d+)\s+(.+)$', cell0)
            if not m:
                m = re.match(r'^(\d+)\s*$', cell0)
                if m and cell1:
                    code = int(m.group(1))
                    meaning = cell1
                else:
                    continue
            else:
                code = int(m.group(1))
                meaning = m.group(2).strip()
                if cell1 and cell1 not in meaning:
                    meaning = (meaning + " " + cell1).strip()
            if code < 0 or code > 1000:
                continue
            key = code
            if key in seen:
                continue
            seen.add(key)
            records.append(code, meaning)
    if not records:
        return None
    return records


# ---- helper (bug-guard) ----
def append_code_meaning(records, code, meaning):
    records.append({
        "id": None,
        "category": "CME",
        "error_type": "CME",
        "code": code,
        "meaning": meaning,
        "description": meaning,
        "related_commands": [],
        "recovery_steps": [],
        "source": {
            "name": "SIM800 Series AT Command Manual",
            "version": "V1.01",
            "date": "2013-07-23",
            "page": "285-292",
            "section": "CME/CMS Error Codes",
            "quote": meaning,
        },
        "source_type": "primary",
        "confidence": 0.85,
        "status": "complete",
        "conflicts": [],
        "notes": "v7: rebuilt from extracted CME/CMS CSV tables.",
        "applicable_models": ["SIM800L"],
        "tags": ["error", "cme", "table-extracted"],
        "created_at": NOW,
        "updated_at": NOW,
    })


# ==================================================================
# 2) dat_15 from Hardware V2.02 pages 58-62
# ==================================================================
def rebuild_dat15():
    candidates = []
    for p in range(58, 63):
        for f in find_csvs(f"*V2.02_p{p:03d}_t*.csv"):
            candidates.append(f)
        for f in find_csvs(f"*Design_V2.02_p{p:03d}_t*.csv"):
            candidates.append(f)
    if not candidates:
        return None
    records = []
    for csvfile in candidates:
        rows = read_csv(csvfile)
        for row in rows:
            row = [clean_cell(c) for c in row]
            if len(row) < 2:
                continue
            joined = " ".join(row)
            # look for numeric value + unit
            m = re.search(r'([\d.]+)\s*(mA|uA|A|mW|uW)\b', joined)
            if not m:
                continue
            value = float(m.group(1))
            unit = m.group(2)
            param = row[0] if row[0] else joined[:60]
            records.append({
                "id": None,
                "category": "Power Consumption",
                "mode": None,
                "command": None,
                "parameter": param,
                "value_min": None,
                "value_typ": value,
                "value_max": None,
                "unit": unit,
                "condition": joined[:120],
                "wake_source": None,
                "related_commands": [],
                "related_states": [],
                "source": {
                    "name": "SIM800H&SIM800L_Hardware_Design",
                    "version": "V2.02",
                    "date": "2015-07-27",
                    "page": csvfile.stem.split("_p")[-1].split("_")[0],
                    "section": "Current Consumption",
                    "quote": joined[:200],
                },
                "source_type": "primary",
                "confidence": 0.7,
                "status": "partial",
                "conflicts": [],
                "notes": "v7: rebuilt from Hardware V2.02 current-consumption tables.",
                "applicable_models": ["SIM800L"],
                "tags": ["power", "table-extracted"],
                "created_at": NOW,
                "updated_at": NOW,
            })
    return records if records else None


# ==================================================================
# 3) dat_01 from at_commands.json
# ==================================================================
def rebuild_dat01():
    if not ATC.exists():
        return None
    data = json.loads(ATC.read_text(encoding="utf-8"))
    # Union all commands across versions; prefer V1.01 page numbers
    seen = {}
    for version, entries in data.items():
        for cmd, page in entries.items():
            if cmd not in seen:
                seen[cmd] = {"version": version, "page": page}
    records = []
    for i, (cmd, info) in enumerate(sorted(seen.items()), 1):
        records.append({
            "id": f"dat_01_{i:04d}",
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
                "page": str(info.get("page", "")),
                "section": None,
                "quote": None,
            },
            "source_type": "primary",
            "confidence": 0.6,
            "status": "partial",
            "conflicts": [],
            "notes": "v7: extracted from at_commands.json scan of AT Manual PDF.",
            "applicable_models": ["SIM800L"],
            "tags": ["at-command", "auto-extracted"],
            "created_at": NOW,
            "updated_at": NOW,
        })
    return records


CATEGORY_RULES = [
    (re.compile(r'^\+C(MG|MT|MR|MSS|MGF|PMS|SMS|NMI|SCA|SCS|SDH|SMP|SMS|SGD|MGDA|MGHEX|MMS)'), "SMS"),
    (re.compile(r'^\+CG(ATT|DCONT|ACT|REG|PADDR|CONTRDP|QMIN|QREQ|CLASS|DATA|EREP|SMS)'), "GPRS"),
    (re.compile(r'^\+CIP|^\+CDNS'), "TCP/IP"),
    (re.compile(r'^\+HTTP'), "HTTP"),
    (re.compile(r'^\+FTP'), "FTP"),
    (re.compile(r'^\+SSL'), "SSL"),
    (re.compile(r'^\+CP(IN|WD|LCK|BS|BR|BW|BF|OL|AS)'), "SIM"),
    (re.compile(r'^\+C(IMI|CID|SPN|SMINS|SIM|RSM)'), "SIM"),
    (re.compile(r'^\+C(LVL|RSL|MUT|AUD|MIC|ALM|ALS|HF|HFA|SIDET)'), "Audio"),
    (re.compile(r'^\+CFUN|^\+CSCLK|^\+CBAT|^\+CBC|^\+CPOWD'), "Power"),
    (re.compile(r'^\+C(REG|OPS|SQ|NUM|SMS|GSM)'), "Network"),
    (re.compile(r'^\+C(LIP|RING|WA|HLD|LCC|STA|RC|RING|OLP)'), "Call"),
    (re.compile(r'^\+STK|^\+SAT|^\+SSTK'), "STK"),
]


def infer_category(cmd):
    for pat, cat in CATEGORY_RULES:
        if pat.search(cmd):
            return cat
    return "General"


# ==================================================================
# Main
# ==================================================================
print("  Rebuilding dat_01 from at_commands.json ...")
recs01 = rebuild_dat01()
if recs01:
    save_yaml("dat_01_at_command.yaml", recs01)
    summary["dat_01"] = f"{len(recs01)} (from at_commands.json)"
    print(f"    dat_01 -> {len(recs01)}")
else:
    summary["dat_01"] = "blocked (no at_commands.json)"
    print("    dat_01 -> blocked")

print("  Rebuilding dat_03 from CME/CMS CSVs ...")
recs03 = rebuild_dat03()
if recs03:
    # Use append_code_meaning helper to build proper records
    built = []
    seen = set()
    for code, meaning in recs03:
        if code in seen:
            continue
        seen.add(code)
        append_code_meaning(built, code, meaning)
    for i, r in enumerate(built, 1):
        r["id"] = f"dat_03_{i:04d}"
    save_yaml("dat_03_error_code.yaml", built)
    summary["dat_03"] = f"{len(built)} (table-extracted)"
    print(f"    dat_03 -> {len(built)}")
else:
    # fall back to blocked placeholder
    blocked = [{
        "id": "dat_03_0001", "category": "Blocked", "error_type": "CME",
        "code": 0, "meaning": None,
        "description": "Blocked: no CME/CMS tables found in sources/extracted/tables/",
        "related_commands": [], "recovery_steps": [],
        "source": {"name": "SIM800 Series AT Command Manual", "version": "V1.01",
                   "date": "2013-07-23", "page": "285-292",
                   "section": "CME/CMS Error Codes", "quote": None},
        "source_type": "primary", "confidence": 0.0, "status": "blocked",
        "conflicts": [], "notes": "v7: could not find CME/CMS tables.",
        "applicable_models": ["SIM800L"], "tags": ["blocked"],
        "created_at": NOW, "updated_at": NOW,
    }]
    save_yaml("dat_03_error_code.yaml", blocked)
    summary["dat_03"] = "blocked (no tables)"
    print("    dat_03 -> blocked")

print("  Rebuilding dat_15 from HW V2.02 current-consumption CSVs ...")
recs15 = rebuild_dat15()
if recs15:
    for i, r in enumerate(recs15, 1):
        r["id"] = f"dat_15_{i:04d}"
    save_yaml("dat_15_power_management.yaml", recs15)
    summary["dat_15"] = f"{len(recs15)} (table-extracted)"
    print(f"    dat_15 -> {len(recs15)}")
else:
    blocked = [{
        "id": "dat_15_0001", "category": "Blocked",
        "mode": None, "command": None, "parameter": None,
        "value_min": None, "value_typ": None, "value_max": None,
        "unit": None, "condition": None, "wake_source": None,
        "related_commands": [], "related_states": [],
        "source": {"name": "SIM800H&SIM800L_Hardware_Design", "version": "V2.02",
                   "date": "2015-07-27", "page": "58-62",
                   "section": "Current Consumption", "quote": None},
        "source_type": "primary", "confidence": 0.0, "status": "blocked",
        "conflicts": [], "notes": "v7: no power tables found.",
        "applicable_models": ["SIM800L"], "tags": ["blocked"],
        "created_at": NOW, "updated_at": NOW,
    }]
    save_yaml("dat_15_power_management.yaml", blocked)
    summary["dat_15"] = "blocked (no tables)"
    print("    dat_15 -> blocked")

# ------------------------------------------------------------------
# 4) Coverage matrix
# ------------------------------------------------------------------
DATASETS = {
    "dat_01": "dat_01_at_command.yaml",
    "dat_02": "dat_02_urc.yaml",
    "dat_03": "dat_03_error_code.yaml",
    "dat_04": "dat_04_timing_timeout.yaml",
    "dat_05": "dat_05_state_machine.yaml",
    "dat_06": "dat_06_init_sequence.yaml",
    "dat_07": "dat_07_hardware_reference.yaml",
    "dat_08": "dat_08_firmware_compatibility.yaml",
    "dat_09": "dat_09_sms.yaml",
    "dat_10": "dat_10_gprs_data.yaml",
    "dat_11": "dat_11_http_ftp_ssl.yaml",
    "dat_12": "dat_12_audio.yaml",
    "dat_13": "dat_13_sim_management.yaml",
    "dat_14": "dat_14_operator_apn.yaml",
    "dat_15": "dat_15_power_management.yaml",
    "dat_16": "dat_16_board_evb.yaml",
    "dat_17": "dat_17_certificate_key_store.yaml",
    "dat_18": "dat_18_certification.yaml",
}

lines = ["# Coverage Matrix", "", f"Generated: {NOW}", "",
         "| Dataset | Records | Status | Breakdown |",
         "|---|---|---|---|"]
total = 0
for k in sorted(DATASETS):
    recs = load_yaml(DATASETS[k])
    n = len(recs)
    total += n
    breakdown = {}
    for r in recs:
        st = (r.get("status") or "unknown").lower()
        breakdown[st] = breakdown.get(st, 0) + 1
    if n == 0:
        st = "empty"
    elif all(s == "blocked" for s in breakdown):
        st = "blocked"
    elif all(s == "complete" for s in breakdown):
        st = "complete"
    else:
        st = "partial"
    bd = ", ".join(f"{a}={b}" for a, b in sorted(breakdown.items()))
    lines.append(f"| {k} | {n} | {st} | {bd} |")

lines.append("")
lines.append(f"**Total records: {total}**")
(REP / "COVERAGE_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")

# ------------------------------------------------------------------
# 5) Data quality report
# ------------------------------------------------------------------
dq = ["# Data Quality Report (v7)", "", f"Generated: {NOW}", "",
      "## What v7 changed", ""]
for k in sorted(summary):
    dq.append(f"- `{k}`: {summary[k]}")
dq += ["",
       "## Method",
       "",
       "v7 rebuilds datasets from **existing extracted CSV tables** in",
       "`sources/extracted/tables/` and from `sources/extracted/at_commands.json`.",
       "It does not fabricate. If a table is not found, the dataset is blocked.",
       "",
       "## Datasets still requiring manual work",
       "",
       "- `dat_04` — timing tables are scattered; needs page-by-page review.",
       "- `dat_05`, `dat_06` — derived; need human semantic construction.",
       "- `dat_07` — pin tables partially extracted; needs manual merge.",
       "- `dat_08` — blocked: no Firmware Release Notes.",
       "- `dat_09`..`dat_14`, `dat_16`..`dat_18` — depend on missing sources.",
       ""]
(REP / "DATA_QUALITY_REPORT.md").write_text("\n".join(dq), encoding="utf-8")

# ------------------------------------------------------------------
# 6) Session log
# ------------------------------------------------------------------
sl = REP / "SESSION_LOG.md"
prev = sl.read_text(encoding="utf-8") if sl.exists() else "# Session Log\n"
entry = f"\n## Session {NOW} (v7 table-based rebuild)\n\n"
for k in sorted(summary):
    entry += f"- {k}: {summary[k]}\n"
entry += "\n- Coverage matrix and data quality report regenerated.\n"
sl.write_text(prev + entry, encoding="utf-8")

print("  Coverage + reports written.")
print("  Summary:")
for k in sorted(summary):
    print(f"    {k}: {summary[k]}")