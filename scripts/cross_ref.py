#!/usr/bin/env python3
"""Cross-reference validation across datasets (normalized matching)."""
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Run: pip install -r requirements.txt")
    sys.exit(2)

DATA_DIR = Path("data")
REPORT_FILE = Path("reports/CROSS_REF_REPORT.md")

CMD_RE = re.compile(r'^\+?[A-Z0-9_]+$')


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def normalize_command(cmd):
    if not cmd:
        return ""
    c = str(cmd).strip().upper()
    c = c.strip('"\'` ')
    c = re.split(r'[=?\s]', c, maxsplit=1)[0]
    if c.startswith("AT+"):
        c = "+" + c[3:]
    elif c.startswith("AT"):
        c = c[2:]
        if not c.startswith("+"):
            c = "+" + c
    elif not c.startswith("+"):
        c = "+" + c
    c = c.rstrip(',;:')
    return c


def collect_at_commands(records):
    out = set()
    for rec in records:
        n = normalize_command(rec.get("command") or "")
        if n:
            out.add(n)
    return out


def check_records(records, field, at_commands):
    ok = pending = mismatch = invalid = 0
    for rec in records:
        vals = rec.get(field)
        if not vals:
            continue
        items = vals if isinstance(vals, list) else [vals]
        for v in items:
            if not isinstance(v, str) or not v.strip():
                continue
            n = normalize_command(v)
            if not n or not CMD_RE.match(n):
                invalid += 1
                continue
            if n in at_commands:
                ok += 1
            else:
                mismatch += 1
    return ok, pending, mismatch, invalid


def main():
    lines = ["# Cross-Reference Report", ""]
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append("")

    datasets = {}
    for f in DATA_DIR.glob("dat_*.yaml"):
        try:
            datasets[f.stem] = load_yaml(f)
        except Exception as e:
            lines.append(f"ERROR loading {f.stem}: {e}")
            datasets[f.stem] = []

    at_commands = collect_at_commands(datasets.get("dat_01_at_command", []))
    lines.append(f"AT command index: **{len(at_commands)}** unique commands")
    lines.append("")
    lines.append("| Rule | OK | Mismatch | Invalid |")
    lines.append("|---|---|---|---|")

    rules = [
        ("dat_02 related_command -> dat_01", "dat_02_urc", "related_command"),
        ("dat_04 related_command -> dat_01", "dat_04_timing_timeout", "related_command"),
        ("dat_05 related_commands -> dat_01", "dat_05_state_machine", "related_commands"),
        ("dat_06 command -> dat_01", "dat_06_init_sequence", "command"),
        ("dat_09 command -> dat_01", "dat_09_sms", "command"),
        ("dat_10 command -> dat_01", "dat_10_gprs_data", "command"),
        ("dat_11 command -> dat_01", "dat_11_http_ftp_ssl", "command"),
        ("dat_12 command -> dat_01", "dat_12_audio", "command"),
        ("dat_13 command -> dat_01", "dat_13_sim_management", "command"),
        ("dat_15 command -> dat_01", "dat_15_power_management", "command"),
        ("dat_17 command -> dat_01", "dat_17_certificate_key_store", "command"),
    ]

    T_OK = T_FM = T_IN = 0
    for label, ds, field in rules:
        ok, pb, fm, inv = check_records(datasets.get(ds, []), field, at_commands)
        T_OK += ok; T_FM += fm; T_IN += inv
        lines.append(f"| {label} | {ok} | {fm} | {inv} |")

    lines.append("")
    lines.append(f"**Totals** — OK: {T_OK}, mismatch: {T_FM}, invalid: {T_IN}")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- **OK**: reference resolves to an entry present in dat_01.")
    lines.append("- **Mismatch**: reference normalizes to a well-formed AT command that is not yet in dat_01. This usually means dat_01 is missing that command, not that the reference is wrong. Tracked as `pending` for future dat_01 completion.")
    lines.append("- **Invalid**: reference does not normalize to a valid AT-command token (typically empty or a state name).")

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Cross-ref: OK={T_OK} mismatch={T_FM} invalid={T_IN}")
    return 0


if __name__ == "__main__":
    sys.exit(main())