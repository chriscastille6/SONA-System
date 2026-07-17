#!/usr/bin/env bash
# Rebuild Appendix B / B2 consent PDFs from Word sources.
#
# Workflow:
#   1. Edit consent_form_pilot.txt or consent_form.txt, then run build_goal_setting_consent_docx.py
#   2. Run: ./scripts/build_consent_from_docx.sh
#   3. Outputs:
#        pdf/ConsentForm_pilot_20260312.pdf
#        pdf/ConsentForm_main_20260312.pdf
#        pdf/ConsentForm_version2_20260312.pdf (alias of main, for legacy references)
#
# Requires LibreOffice (macOS default path below). Install from https://www.libreoffice.org if missing.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MATERIALS_DIR="$REPO_ROOT/apps/studies/assets/irb/goal-setting/materials"
PDF_DIR="$MATERIALS_DIR/pdf"

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

convert_docx() {
  local docx="$1"
  local out_pdf="$2"
  if [[ ! -f "$docx" ]]; then
    echo "error: consent source not found: $docx" >&2
    exit 1
  fi
  mkdir -p "$PDF_DIR"
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN
  echo "Converting $docx -> $out_pdf (via LibreOffice)"
  "$SOFFICE" --headless --convert-to pdf --outdir "$tmp_dir" "$docx" >/dev/null 2>&1
  local generated="$tmp_dir/$(basename "${docx%.docx}.pdf")"
  if [[ ! -f "$generated" ]]; then
    echo "error: LibreOffice did not produce a PDF for $docx" >&2
    exit 1
  fi
  mv -f "$generated" "$out_pdf"
  echo "Wrote $out_pdf"
}

# Ensure .docx files exist (build from .txt if needed).
if [[ ! -f "$MATERIALS_DIR/consent_form_pilot.docx" || ! -f "$MATERIALS_DIR/consent_form.docx" ]]; then
  python3 "$REPO_ROOT/scripts/build_goal_setting_consent_docx.py"
fi

convert_docx "$MATERIALS_DIR/consent_form_pilot.docx" "$PDF_DIR/ConsentForm_pilot_20260312.pdf"
convert_docx "$MATERIALS_DIR/consent_form.docx" "$PDF_DIR/ConsentForm_main_20260312.pdf"
cp -f "$PDF_DIR/ConsentForm_main_20260312.pdf" "$PDF_DIR/ConsentForm_version2_20260312.pdf"
echo "Wrote alias $PDF_DIR/ConsentForm_version2_20260312.pdf"
