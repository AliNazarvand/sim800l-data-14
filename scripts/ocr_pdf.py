#!/usr/bin/env python3
"""OCR fallback for scanned PDFs (uses pytesseract)."""
import sys
from pathlib import Path

try:
    import pytesseract
    from pdf2image import convert_from_path
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

SOURCES_DIR = Path("sources/originals")
OUTPUT_DIR = Path("sources/extracted")


def ocr_pdf(pdf_path, output_dir, lang="eng", dpi=300):
    if not HAS_OCR:
        print("pytesseract/pdf2image missing. Run: pip install -r requirements.txt")
        return False
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / (pdf_path.stem + ".ocr.txt")
    images = convert_from_path(str(pdf_path), dpi=dpi)
    parts = []
    for i, img in enumerate(images):
        txt = pytesseract.image_to_string(img, lang=lang)
        parts.append(f"--- OCR Page {i + 1} ---\n{txt}")
    out_file.write_text("\n".join(parts), encoding="utf-8")
    print(f"OCR -> {out_file}")
    return True


def main():
    if not HAS_OCR:
        print("OCR stack unavailable.")
        return 2
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = list(SOURCES_DIR.glob("*.pdf")) + list(SOURCES_DIR.glob("*.PDF"))
    if not pdfs:
        print("No PDFs to OCR.")
        return 1
    for p in pdfs:
        print(f"OCR: {p.name}")
        ocr_pdf(p, OUTPUT_DIR)
    print("OCR complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())