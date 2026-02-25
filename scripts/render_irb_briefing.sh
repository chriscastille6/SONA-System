#!/bin/bash
# Generate IRB briefing PDF from JSON (mirrors Psychological Assessments FERPA workflow)
# 1. JSON → HTML (Python)
# 2. HTML → PDF (Puppeteer)
#
# Usage: ./scripts/render_irb_briefing.sh

set -e
cd "$(dirname "$0")/.."

echo "1. Generating HTML from JSON..."
python3 scripts/generate_irb_briefing_html.py

echo "2. Generating PDF from HTML..."
cd scripts && node generate_irb_briefing_pdf.js

echo ""
echo "Output: IRB_BRIEFING_JULIANN_JON.pdf"
