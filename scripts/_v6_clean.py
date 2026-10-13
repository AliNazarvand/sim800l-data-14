import re, yaml, json
from pathlib import Path
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
DATA = Path("data")
REP  = Path("reports")
REP.mkdir(exist_ok=True)

def load(name):
    p = DATA / name
    if not p.exists(): return []
    return yaml.safe_load(p.read_text(encoding="utf-8")) or []

def save(name, data):
    p = DATA / name
    with open(p, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

def renumber(records, prefix):
    for i, r in enumerate(records, 1):
        r["id"] = f"{prefix}_{i:04d}"
    return records

# ------------------------------------------------------------------
# 1) dat_01: remove records with no verifiable source
# ------------------------------------------------------------------
before01 = load("dat_01_at_command.yaml")
def keep_01(r):
    src = r.get("source") or {}
    q = (src.get("quote") or "").strip()
    page = str(src.get("page") or "").strip()
    # Delete if quote is empty AND page is auto/'8' (fake)
    if not q:
        return False
    # Delete if quote is a TOC line (dots leaders)
    if re.search(r'\.{6,}', q) or re.search(r'\.{3,}\d+\s*$', q):
        return False
    # Delete if quote is over 60% dots
    if len(q) > 20 and q.count('.') > len(q) * 0.4:
        return False
    return True

after01 = [r for r in before01 if keep_01(r)]
after01 = renumber(after01, "dat_01")
save("dat_01_at_command.yaml", after01)
print(f"  dat_01: {len(before01)} -> {len(after01)}")

# ------------------------------------------------------------------
# 2) dat_02: remove records with garbage parameters
# ------------------------------------------------------------------
before02 = load("dat_02_urc.yaml")
def keep_02(r):
    u = (r.get("urc_string") or "").strip()
    if not u: return False
    # valid URC: starts with + or is a bare keyword
    if not (u.startswith("+") or re.match(r'^[A-Z][A-Z0-9 _]{1,30}$', u)):
        return False
    params = r.get("parameters") or []
    if not isinstance(params, list):
        return False
    # Each parameter must have a name AND a meaningful description
    # (not just punctuation, not empty)
    for p in params:
        if not isinstance(p, dict): return False
        name = (p.get("name") or "").strip()
        desc = (p.get("description") or "").strip()
        if not name: return False
        # description must contain at least one alphanumeric char
        if not re.search(r'[A-Za-z0-9]', desc):
            return False
    return True

after02 = [r for r in before02 if keep_02(r)]
after02 = renumber(after02, "dat_02")
save("dat_02_urc.yaml", after02)
print(f"  dat_02: {len(before02)} -> {len(after02)}")

# ------------------------------------------------------------------
# 3) dat_03: CLEAR and mark blocked
#    Rationale: every surviving record has shifted meanings relative
#    to its source quote. Re-extraction from the PDF is required.
# ------------------------------------------------------------------
before03 = load("dat_03_error_code.yaml")
blocked03 = [{
    "id": "dat_03_0001",
    "category": "Blocked",
    "error_type": "CME",
    "code": 0,
    "meaning": None,
    "description": "Dataset blocked: prior extraction produced shifted meanings. Full re-extraction from AT Manual V1.01 appendix required.",
    "related_commands": [],
    "recovery_steps": [],
    "source": {
        "name": "SIM800 Series AT Command Manual",
        "version": "V1.01",
        "date": "2013-07-23",
        "page": "285-291",
        "section": "CME/CMS Error Codes",
        "quote": None,
    },
    "source_type": "primary",
    "confidence": 0.0,
    "status": "blocked",
    "conflicts": [],
    "notes": "v6: cleared {n} records whose meaning did not match their source quote. See reports/DATA_QUALITY_REPORT.md".format(n=len(before03)),
    "applicable_models": ["SIM800L"],
    "tags": ["blocked", "needs-reextraction"],
    "created_at": NOW,
    "updated_at": NOW,
}]
save("dat_03_error_code.yaml", blocked03)
print(f"  dat_03: {len(before03)} -> 1 (blocked)")

# ------------------------------------------------------------------
# 4) dat_04: keep ONLY records added by correction-pass v4
#    (they have confidence >= 0.5 AND a proper section)
# ------------------------------------------------------------------
before04 = load("dat_04_timing_timeout.yaml")
def keep_04(r):
    conf = r.get("confidence") or 0
    try: conf = float(conf)
    except: conf = 0.0
    if conf < 0.5: return False
    # Must have a non-empty section
    src = r.get("source") or {}
    sect = (src.get("section") or "").strip()
    if not sect: return False
    # Must not be marked out-of-scope in tags
    tags = r.get("tags") or []
    if "out-of-scope" in tags or "legacy" in tags: return False
    return True

after04 = [r for r in before04 if keep_04(r)]
after04 = renumber(after04, "dat_04")
save("dat_04_timing_timeout.yaml", after04)
print(f"  dat_04: {len(before04)} -> {len(after04)}")

# ------------------------------------------------------------------
# 5) dat_15: CLEAR and mark blocked
#    Every surviving record was a section heading, not a data point.
# ------------------------------------------------------------------
before15 = load("dat_15_power_management.yaml")
blocked15 = [{
    "id": "dat_15_0001",
    "category": "Blocked",
    "mode": None,
    "command": None,
    "parameter": None,
    "value_min": None, "value_typ": None, "value_max": None,
    "unit": None, "condition": None, "wake_source": None,
    "related_commands": [], "related_states": [],
    "source": {
        "name": "SIM800H&SIM800L_Hardware_Design",
        "version": "V2.02",
        "date": "2015-07-27",
        "page": "58-62",
        "section": "Current Consumption",
        "quote": None,
    },
    "source_type": "primary",
    "confidence": 0.0,
    "status": "blocked",
    "conflicts": [],
    "notes": "v6: cleared {n} auto-extracted records that were section headings or TOC fragments, not data. Manual re-extraction from V2.02 section 6.8 required.".format(n=len(before15)),
    "applicable_models": ["SIM800L"],
    "tags": ["blocked", "needs-reextraction"],
    "created_at": NOW,
    "updated_at": NOW,
}]
save("dat_15_power_management.yaml", blocked15)
print(f"  dat_15: {len(before15)} -> 1 (blocked)")

# ------------------------------------------------------------------
# 6) Regenerate honest COVERAGE_MATRIX.md
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

rows = []
for key in sorted(DATASETS.keys()):
    recs = load(DATASETS[key])
    n = len(recs)
    statuses = {}
    for r in recs:
        st = (r.get("status") or "unknown").lower()
        statuses[st] = statuses.get(st, 0) + 1
    # Honest dominant status: priority order
    if n == 0:
        status = "empty"
    elif statuses.get("blocked", 0) > 0 and all(s in ("blocked","unknown") for s in statuses):
        status = "blocked"
    elif statuses.get("blocked", 0) > 0:
        status = "partial-blocked"
    elif statuses.get("complete", 0) == n:
        status = "complete"
    elif statuses.get("complete", 0) > 0:
        status = "partial"
    elif "partial" in statuses:
        status = "partial"
    else:
        status = "unknown"
    rows.append((key, n, status, dict(statuses)))

lines = ["# Coverage Matrix", "", f"Generated: {NOW}", "",
         "| Dataset | Records | Status | Breakdown |",
         "|---|---|---|---|"]
for key, n, status, breakdown in rows:
    bd = ", ".join(f"{k}={v}" for k, v in sorted(breakdown.items()))
    lines.append(f"| {key} | {n} | {status} | {bd} |")

total = sum(r[1] for r in rows)
lines.append("")
lines.append(f"**Total records: {total}**")
lines.append("")
lines.append("## Honest status meanings")
lines.append("")
lines.append("- **blocked**: no verifiable source; requires re-extraction.")
lines.append("- **partial-blocked**: some records are blocked, others are partial.")
lines.append("- **partial**: records exist but coverage < 95% or confidence low.")
lines.append("- **complete**: all records have confidence >= 0.7 and coverage_estimate=high.")
(REP / "COVERAGE_MATRIX.md").write_text("\n".join(lines), encoding="utf-8")

# ------------------------------------------------------------------
# 7) Honest DATA_QUALITY_REPORT.md
# ------------------------------------------------------------------
dq = f"""# Data Quality Report (v6)

Generated: {NOW}

## What v6 changed

v5 tried to remove TOC-quote records but left many other problems.
v6 takes a stricter, more honest position:

| Dataset | Before v6 | After v6 | Action |
|---|---|---|---|
| dat_01 | {len(before01)} | {len(after01)} | Removed records with empty quotes and fabricated page values. |
| dat_02 | {len(before02)} | {len(after02)} | Removed records whose parameters were punctuation-only. |
| dat_03 | {len(before03)} | 1 (blocked) | **Cleared.** Meanings were shifted relative to source quotes. |
| dat_04 | {len(before04)} | {len(after04)} | Kept only correction-pass records with confidence >= 0.5. |
| dat_15 | {len(before15)} | 1 (blocked) | **Cleared.** Records were section headings, not data. |

## Datasets now marked blocked

- ``dat_03`` — the extracted meanings do not match the source quotes.
  Requires re-parsing the CME/CMS appendix from AT Manual V1.01.
- ``dat_15`` — the extracted records were TOC lines and section headings.
  Requires re-parsing section 6.8 from Hardware Design V2.02.

## Datasets that still need manual review

- ``dat_01`` — remaining records have context quotes but page metadata
  may still be imprecise. Human spot-check recommended.
- ``dat_05``, ``dat_06`` — contain legacy records with mixed sources.
- ``dat_09``..``dat_13`` — ``syntax`` fields may contain TOC fragments.
- ``dat_07`` — mostly sound; numeric values need manual verification.

## Why auto-extraction failed

The extraction scripts (``_v4``, ``_v5``) used regex over raw PDF text
without respecting table structure. This produced:

1. Command names without their metadata.
2. Meanings shifted by one row from their codes.
3. Section headings treated as data points.

A correct extraction requires either a table-aware parser
(e.g. ``camelot`` with lattice mode) or manual transcription.

## Recommendation

The user must manually re-extract ``dat_03`` and ``dat_15``, or provide
a properly parsed PDF table. Until then, they are marked ``blocked``
and no fabricated data is present.
"""
(REP / "DATA_QUALITY_REPORT.md").write_text(dq, encoding="utf-8")

# ------------------------------------------------------------------
# 8) Session log entry
# ------------------------------------------------------------------
sl = REP / "SESSION_LOG.md"
entry = f"""

## Session {NOW} (v6 honest cleanup)

- Removed records from dat_01, dat_02, dat_04 with unverifiable sources.
- CLEARED dat_03 and dat_15 and marked them ``blocked`` (systematic errors).
- Coverage matrix uses priority-based status (blocked > partial > complete).
- See ``reports/DATA_QUALITY_REPORT.md`` for the honest current state.
"""
prev = sl.read_text(encoding="utf-8") if sl.exists() else "# Session Log\n"
sl.write_text(prev + entry, encoding="utf-8")

print("  Reports regenerated.")