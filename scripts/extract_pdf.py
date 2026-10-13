#!/usr/bin/env python3
"""Extract text and tables from PDF sources using pdfplumber."""
import sys
from pathlib import Path

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

SOURCES_DIR = Path("sources/originals")
EXTRACTED_DIR = Path("sources/extracted")
TABLES_DIR = EXTRACTED_DIR / "tables"


def extract_text(pdf_path, output_dir):
    if not HAS_PDFPLUMBER:
        print("pdfplumber missing. Run: pip install -r requirements.txt")
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    text_file = output_dir / (pdf_path.stem + ".txt")
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append(f"--- Page {i + 1} ---\n{text}")
        text_file.write_text("\n".join(pages), encoding="utf-8")
    print(f"  text  -> {text_file}")
    return True


def extract_tables(pdf_path, output_dir):
    if not HAS_PDFPLUMBER:
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables() or []
            for j, table in enumerate(tables):
                out = output_dir / f"{pdf_path.stem}_p{i + 1:03d}_t{j + 1:02d}.csv"
                with open(out, "w", encoding="utf-8") as f:
                    for row in table:
                        f.write(",".join((str(c) if c is not None else "") for c in row) + "\n")
                count += 1
    print(f"  tables-> {count} files")
    return True


def main():
    if not HAS_PDFPLUMBER:
        print("pdfplumber not available; install requirements first.")
        return 2
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = list(SOURCES_DIR.glob("*.pdf")) + list(SOURCES_DIR.glob("*.PDF"))
    if not pdfs:
        print(f"No PDFs in {SOURCES_DIR}")
        return 1
    for pdf in pdfs:
        print(f"Processing: {pdf.name}")
        extract_text(pdf, EXTRACTED_DIR)
        extract_tables(pdf, TABLES_DIR)
    print("Extraction complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())