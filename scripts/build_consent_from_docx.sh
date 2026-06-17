#!/usr/bin/env bash
# Rebuild Appendix B consent PDF from the Word source (consent_form.docx).
#
# Workflow:
#   1. Edit apps/studies/assets/irb/goal-setting/materials/consent_form.docx in Word.
#   2. Run: ./scripts/build_consent_from_docx.sh
#   3. Output: materials/pdf/ConsentForm_version2_20260312.pdf (merged into HSIRB packet as Appendix B)
#
# Requires LibreOffice (macOS default path below). Install from https://www.libreoffice.org if missing.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATERIALS_DIR="$REPO_ROOT/apps/studies/assets/irb/goal-setting/materials"
DOCX="$MATERIALS_DIR/consent_form.docx"
OUT_PDF="$MATERIALS_DIR/pdf/ConsentForm_version2_20260312.pdf"
PDF_DIR="$MATERIALS_DIR/pdf"

if [[ ! -f "$DOCX" ]]; then
  echo "error: consent source not found: $DOCX" >&2
  exit 1
fi

SOFFICE=""
for candidate in \
  "/Applications/LibreOffice.app/Contents/MacOS/soffice" \
  "$(command -v soffice 2>/dev/null || true)"; do
  if [[ -n "$candidate" && -x "$candidate" ]]; then
    SOFFICE="$candidate"
    break
  fi
done

if [[ -z "$SOFFICE" ]]; then
  echo "error: LibreOffice (soffice) not found. Install LibreOffice or set SOFFICE to its path." >&2
  exit 1
fi

mkdir -p "$PDF_DIR"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Converting $DOCX -> $OUT_PDF (via LibreOffice)"
"$SOFFICE" --headless --convert-to pdf --outdir "$TMP_DIR" "$DOCX" >/dev/null 2>&1

GENERATED="$TMP_DIR/$(basename "${DOCX%.docx}.pdf")"
if [[ ! -f "$GENERATED" ]]; then
  echo "error: LibreOffice did not produce a PDF in $TMP_DIR" >&2
  exit 1
fi

mv -f "$GENERATED" "$OUT_PDF"
echo "Wrote $OUT_PDF"
