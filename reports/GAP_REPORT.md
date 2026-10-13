# Gap Report

Generated: 2026-10-13T19:33:28Z

## Missing sources

| Missing | Affected datasets | Impact |
|---|---|---|
| SIM800 Series TCP/IP AT Command Manual | dat_10 | pending cross-refs |
| SIM800 Series HTTP AT Command Manual | dat_11 | pending cross-refs |
| SIM800 Series FTP AT Command Manual | dat_11 | pending cross-refs |
| SIM800 Series SSL AT Command Manual | dat_11, dat_17 | pending cross-refs |
| SIM800 Series Audio AT Command Manual | dat_12 | pending cross-refs |
| SIM800 Series SIM AT Command Manual | dat_13 | pending cross-refs |
| SIM800 Series Firmware Release Notes | dat_08 | blocked |
| SIM800 Series Certification Documents | dat_18 | blocked |
| Official EVB documentation | dat_16 | blocked |

## Resolution plan

1. Place the missing PDF in `sources/originals/`.
2. Run `python scripts/extract_pdf.py` (or `ocr_pdf.py` for scans).
3. Re-audit the affected dataset.
4. Re-run `python scripts/validate.py` and `cross_ref.py`.