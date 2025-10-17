#!/bin/bash
# IRB Package Generation Script
# Automates the complete IRB application generation process

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
CONFIG_FILE=""
APP_DIR=""
OUTPUT_DIR="irb_output"
SERVER_PORT=8080
SKIP_SCREENSHOTS=false
SKIP_PDF=false

# Print usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --config FILE       Path to config JSON file (required)"
    echo "  --app-dir DIR       Directory containing web application"
    echo "  --output-dir DIR    Output directory (default: irb_output)"
    echo "  --port PORT         Server port (default: 8080)"
    echo "  --skip-screenshots  Skip screenshot capture"
    echo "  --skip-pdf          Skip PDF generation"
    echo "  -h, --help          Show this help message"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --app-dir)
            APP_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --port)
            SERVER_PORT="$2"
            shift 2
            ;;
        --skip-screenshots)
            SKIP_SCREENSHOTS=true
            shift
            ;;
        --skip-pdf)
            SKIP_PDF=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [ -z "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: --config is required${NC}"
    usage
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Config file not found: $CONFIG_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}=== IRB Package Generation ===${NC}"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/screenshots"
echo -e "${GREEN}✓${NC} Created output directory: $OUTPUT_DIR"

# Step 1: Start server (if app directory provided)
SERVER_PID=""
if [ ! -z "$APP_DIR" ] && [ "$SKIP_SCREENSHOTS" = false ]; then
    echo ""
    echo -e "${BLUE}Step 1: Starting local server...${NC}"
    cd "$APP_DIR"
    python3 -m http.server $SERVER_PORT --directory . &
    SERVER_PID=$!
    sleep 2
    echo -e "${GREEN}✓${NC} Server running on port $SERVER_PORT (PID: $SERVER_PID)"
    cd - > /dev/null
fi

# Step 2: Capture screenshots
if [ "$SKIP_SCREENSHOTS" = false ]; then
    echo ""
    echo -e "${BLUE}Step 2: Capturing screenshots...${NC}"
    python3 "$(dirname "$0")/capture_screenshots.py" \
        --config "$CONFIG_FILE" \
        --output "$OUTPUT_DIR/screenshots"
    echo -e "${GREEN}✓${NC} Screenshots captured"
fi

# Step 3: Stop server
if [ ! -z "$SERVER_PID" ]; then
    echo ""
    echo -e "${BLUE}Step 3: Stopping server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Server stopped"
fi

# Step 4: Generate IRB documents
if [ "$SKIP_PDF" = false ]; then
    echo ""
    echo -e "${BLUE}Step 4: Generating IRB documents...${NC}"
    
    # Copy template to output directory
    TEMPLATE_DIR="$(dirname "$0")/../templates"
    cp "$TEMPLATE_DIR/IRB_Application_Template.Rmd" "$OUTPUT_DIR/"
    
    # Copy screenshots to relative path expected by template
    cp -r "$OUTPUT_DIR/screenshots" "$OUTPUT_DIR/../"
    
    # Generate PDF
    cd "$OUTPUT_DIR"
    R -e "rmarkdown::render('IRB_Application_Template.Rmd', output_format = rmarkdown::pdf_document(latex_engine = 'xelatex'))" 2>&1 | grep -E "(processing|Output created|Error)" || true
    
    # Generate Word
    R -e "rmarkdown::render('IRB_Application_Template.Rmd', output_format = 'word_document')" 2>&1 | grep -E "(processing|Output created|Error)" || true
    
    cd - > /dev/null
    echo -e "${GREEN}✓${NC} IRB documents generated"
fi

# Step 5: Create package summary
echo ""
echo -e "${BLUE}Step 5: Creating package summary...${NC}"

cat > "$OUTPUT_DIR/PACKAGE_CONTENTS.md" << EOF
# IRB Application Package

**Generated:** $(date)
**Config:** $CONFIG_FILE

## Contents

### Documents
- IRB_Application_Template.pdf - Main IRB application (PDF)
- IRB_Application_Template.docx - Main IRB application (Word)
- IRB_Application_Template.Rmd - Source template

### Screenshots
$(ls -1 "$OUTPUT_DIR/screenshots" 2>/dev/null | while read file; do echo "- $file"; done)

### Configuration
- Config file: $CONFIG_FILE

## Next Steps

1. Review IRB_Application_Template.pdf
2. Verify all screenshots are clear and complete
3. Update any placeholder text in the template
4. Print and sign signature pages
5. Submit to HSIRB

## Files Summary
EOF

# Add file sizes
echo "" >> "$OUTPUT_DIR/PACKAGE_CONTENTS.md"
echo "### File Sizes" >> "$OUTPUT_DIR/PACKAGE_CONTENTS.md"
if [ -f "$OUTPUT_DIR/IRB_Application_Template.pdf" ]; then
    PDF_SIZE=$(ls -lh "$OUTPUT_DIR/IRB_Application_Template.pdf" | awk '{print $5}')
    echo "- PDF: $PDF_SIZE" >> "$OUTPUT_DIR/PACKAGE_CONTENTS.md"
fi
if [ -f "$OUTPUT_DIR/IRB_Application_Template.docx" ]; then
    DOCX_SIZE=$(ls -lh "$OUTPUT_DIR/IRB_Application_Template.docx" | awk '{print $5}')
    echo "- Word: $DOCX_SIZE" >> "$OUTPUT_DIR/PACKAGE_CONTENTS.md"
fi

echo -e "${GREEN}✓${NC} Package summary created"

# Final summary
echo ""
echo -e "${GREEN}=== Generation Complete ===${NC}"
echo ""
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Files created:"
[ -f "$OUTPUT_DIR/IRB_Application_Template.pdf" ] && echo "  ✓ IRB_Application_Template.pdf"
[ -f "$OUTPUT_DIR/IRB_Application_Template.docx" ] && echo "  ✓ IRB_Application_Template.docx"
echo "  ✓ Screenshots: $(ls -1 "$OUTPUT_DIR/screenshots" 2>/dev/null | wc -l | tr -d ' ') files"
echo "  ✓ PACKAGE_CONTENTS.md"
echo ""
echo "Next steps:"
echo "  1. Review PDF: open $OUTPUT_DIR/IRB_Application_Template.pdf"
echo "  2. Read summary: cat $OUTPUT_DIR/PACKAGE_CONTENTS.md"
echo ""

