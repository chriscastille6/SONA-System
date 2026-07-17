#!/usr/bin/env bash
# Rebuild Appendix C workbook HSIRB sample PDF from cash print master.
# Extracts pages 1-17 (first complete do-your-best block incl. Round #8 RAVOLET).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATERIALS_DIR="$REPO_ROOT/apps/studies/assets/irb/goal-setting/materials"
DOCX="$MATERIALS_DIR/admin/workbooks_cash_no_computers_v2.docx"
OUT_PDF="$MATERIALS_DIR/pdf/Workbook_version2_20260312.pdf"
SAMPLE_PAGES=17

SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
[[ -x "$SOFFICE" ]] || { echo "LibreOffice not found" >&2; exit 1; }

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

"$SOFFICE" --headless --convert-to pdf --outdir "$TMP_DIR" "$DOCX" >/dev/null 2>&1
FULL_PDF="$(find "$TMP_DIR" -maxdepth 1 -name '*.pdf' -print -quit)"

python3 - "$FULL_PDF" "$OUT_PDF" "$SAMPLE_PAGES" <<'PY'
import sys
import fitz

full_path, out_path, sample_pages = sys.argv[1:4]
sample_pages = int(sample_pages)
src = fitz.open(full_path)
dst = fitz.open()
dst.insert_pdf(src, from_page=0, to_page=sample_pages - 1)
dst.save(out_path)
page_count = len(dst)
dst.close()
src.close()
print(f"Wrote {out_path} ({page_count} pages from {full_path})")
PY
