#!/usr/bin/env bash
# Rebuild Appendix C workbook PDF from Word source.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATERIALS_DIR="$REPO_ROOT/apps/studies/assets/irb/goal-setting/materials"
DOCX="$MATERIALS_DIR/Workbook_version2_20260312.docx"
OUT_PDF="$MATERIALS_DIR/pdf/Workbook_version2_20260312.pdf"

SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
[[ -x "$SOFFICE" ]] || { echo "LibreOffice not found" >&2; exit 1; }

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

"$SOFFICE" --headless --convert-to pdf --outdir "$TMP_DIR" "$DOCX" >/dev/null 2>&1
mv -f "$TMP_DIR/Workbook_version2_20260312.pdf" "$OUT_PDF"
echo "Wrote $OUT_PDF"
