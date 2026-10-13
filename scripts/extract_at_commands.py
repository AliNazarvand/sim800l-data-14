#!/usr/bin/env python3
"""Extract AT commands from PDF manuals using pdfplumber.

Scans all PDFs in sources/originals/ matching *AT Command Manual* and
extracts all AT+XXX patterns, producing sources/extracted/at_commands.json
with format: { "version": { "+CMD": first_page_seen, ... } }
"""
import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("pdfplumber missing. pip install -r requirements.txt")
    sys.exit(2)

SOURCES_DIR = Path("sources/originals")
OUTPUT = Path("sources/extracted/at_commands.json")

CMD_PAT = re.compile(r'\bAT\+([A-Z][A-Z0-9_]{1,20})\b')
VERSION_PAT = re.compile(r'[Vv](\d+\.\d+)')


def detect_version(name):
    m = VERSION_PAT.search(name)
    return f"V{m.group(1)}" if m else "unknown"


def scan_pdf(path):
    cmds = {}
    try:
        with pdfplumber.open(str(path)) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    continue
                for m in CMD_PAT.finditer(text):
                    cmd = "+" + m.group(1)
                    if cmd not in cmds:
                        cmds[cmd] = i + 1
    except Exception as e:
        print(f"  ERROR reading {path.name}: {e}")
    return cmds


def main():
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(list(SOURCES_DIR.glob("*AT Command Manual*.pdf")))
    if not pdfs:
        print("No AT Command Manual PDFs found.")
        return 1

    result = {}
    for pdf in pdfs:
        version = detect_version(pdf.name)
        print(f"  Scanning {pdf.name} (version={version})...")
        cmds = scan_pdf(pdf)
        print(f"    -> {len(cmds)} commands")
        # If duplicate version, keep richer set
        if version in result:
            for k, v in cmds.items():
                if k not in result[version]:
                    result[version][k] = v
        else:
            result[version] = cmds

    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    total = sum(len(v) for v in result.values())
    print(f"Total: {len(result)} versions, {total} command-entries saved to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())