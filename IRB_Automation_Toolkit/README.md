# IRB Automation Toolkit

**Version:** 1.0  
**Date:** October 2025  
**Institution:** Nicholls State University  
**Purpose:** Automated tools for IRB application generation and screenshot capture

---

## Overview

This toolkit automates the creation of IRB applications with embedded screenshots for research projects at Nicholls State University.

It provides:
- Screenshot capture automation for web applications
- IRB document generation (PDF + Word)
- Nicholls HSIRB formatting templates
- Verification and validation scripts

---

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install selenium

# Ensure R and required packages are installed
R -e "install.packages(c('rmarkdown', 'knitr'))"
```

### 2. Customize Template

Edit `templates/IRB_Application_Template.Rmd` with your project details:
- PI name and contact
- Project title
- Study description
- Population details
- Data collection methods

### 3. Add Your Screenshots

Place your web application files in a directory, then:

```bash
# Start local server
python3 -m http.server 8080 --directory /path/to/your/app

# Run screenshot capture (in new terminal)
python3 scripts/capture_screenshots.py --config your_config.json
```

### 4. Generate IRB Documents

```bash
# Generate PDF and Word documents
cd templates/
R -e "rmarkdown::render('IRB_Application_Template.Rmd', output_format = 'all')"
```

---

## Directory Structure

```
IRB_Automation_Toolkit/
├── README.md                    # This file
├── SETUP.md                     # Detailed setup instructions
├── templates/
│   ├── IRB_Application_Template.Rmd        # Main IRB template (Nicholls format)
│   ├── IRB_Exempt_Template.Rmd             # Exempt review template
│   ├── screenshot_appendix_template.html   # HTML screenshot appendix
│   └── consent_form_template.md            # Informed consent template
├── scripts/
│   ├── capture_screenshots.py              # Automated screenshot capture
│   ├── capture_choice_task.py              # Specialized choice task capture
│   ├── verify_formatting.py                # PDF formatting verification
│   └── generate_irb_package.sh             # Full automation script
├── configs/
│   ├── example_config.json                 # Example configuration
│   └── nicholls_hsirb_settings.json        # Nicholls-specific settings
├── examples/
│   ├── conjoint_analysis_example/          # Complete example
│   └── sample_outputs/                     # Sample generated files
└── docs/
    ├── NICHOLLS_IRB_GUIDE.md               # Nicholls IRB process guide
    ├── SCREENSHOT_GUIDE.md                 # Screenshot best practices
    └── FORMATTING_STANDARDS.md             # Nicholls formatting requirements
```

---

## Features

### 1. Screenshot Automation
- Headless browser capture (Selenium + Chrome)
- Configurable viewports and scroll positions
- Automatic naming and organization
- Support for interactive elements

### 2. IRB Document Generation
- R Markdown to PDF (xelatex engine)
- R Markdown to Word (pandoc)
- Embedded screenshots (full-width, auto-sized)
- Nicholls HSIRB formatting (Times New Roman, single-spaced, HSIRB page markers)

### 3. Templates
- **Non-Exempt Review:** Full Nicholls template with procedural preface
- **Exempt Review:** Simplified template for exempt studies
- **Consent Forms:** Standard informed consent templates
- **Screenshot Appendix:** HTML template with image placeholders

### 4. Verification Tools
- PDF formatting checker
- Screenshot quality validator
- Completeness checklist
- Budget verification (for economics studies)

---

## Configuration

### Screenshot Config (JSON)

```json
{
  "server_url": "http://localhost:8080",
  "screenshots": [
    {
      "name": "welcome_page",
      "path": "/index.html",
      "viewport": {"width": 1400, "height": 900},
      "scroll": 0,
      "wait": 3
    },
    {
      "name": "choice_task",
      "path": "/survey.html",
      "viewport": {"width": 1400, "height": 1100},
      "scroll": 0,
      "wait": 2,
      "javascript": "document.getElementById('startBtn').click();"
    }
  ],
  "output_dir": "screenshots"
}
```

### IRB Settings (JSON)

```json
{
  "institution": "Nicholls State University",
  "irb_type": "non-exempt",
  "review_category": "expedited",
  "formatting": {
    "font": "Times New Roman",
    "font_size": "12pt",
    "line_spacing": "single",
    "margins": "1in",
    "page_markers": "HSIRB"
  }
}
```

---

## Workflow

### Typical IRB Application Process

1. **Prepare** your web application/survey
2. **Configure** screenshot capture settings
3. **Capture** screenshots automatically
4. **Customize** IRB template with your study details
5. **Generate** PDF and Word documents
6. **Verify** formatting matches Nicholls standards
7. **Submit** to HSIRB

### Full Automation (Advanced)

```bash
# Single command to generate complete IRB package
./scripts/generate_irb_package.sh \
  --app-dir /path/to/your/app \
  --config configs/your_config.json \
  --output-dir output/
```

This will:
1. Start local server
2. Capture all screenshots
3. Generate IRB documents (PDF + Word)
4. Create screenshot appendix
5. Verify formatting
6. Package everything for submission

---

## Templates Included

### 1. Non-Exempt IRB Application
**File:** `templates/IRB_Application_Template.Rmd`

**Features:**
- Nicholls HSIRB standard format
- Procedural preface (4-item list)
- Form-style field layout
- HSIRB page markers
- Times New Roman 12pt, single-spaced
- Appendices: Consent, Instruments, Technical Specs, Assessment Items, Screenshots

**Customization points:**
- Line 18: PI name and phone
- Line 21: Co-investigators
- Line 30: Project title
- Lines 37-100: Study description
- Lines 250+: Appendices content

### 2. Exempt IRB Template
**File:** `templates/IRB_Exempt_Template.Rmd`

**Features:**
- Simplified format for exempt studies
- Educational setting justification
- Minimal risk documentation

### 3. Screenshot Appendix
**File:** `templates/screenshot_appendix_template.html`

**Features:**
- Professional HTML layout
- Image placeholders
- Description sections
- Print-ready styling

---

## Scripts

### 1. capture_screenshots.py

**Purpose:** Automated screenshot capture using Selenium

**Usage:**
```bash
python3 scripts/capture_screenshots.py --config config.json
```

**Features:**
- Headless Chrome automation
- Configurable viewports
- JavaScript injection support
- Automatic retry on failure
- Quality validation

### 2. capture_choice_task.py

**Purpose:** Specialized capture for choice tasks / interactive elements

**Usage:**
```bash
python3 scripts/capture_choice_task.py \
  --url http://localhost:8080/survey.html \
  --output screenshots/choice_task.png
```

### 3. verify_formatting.py

**Purpose:** Verify PDF matches Nicholls formatting standards

**Usage:**
```bash
python3 scripts/verify_formatting.py --pdf your_irb.pdf
```

**Checks:**
- Font: Times New Roman
- Font size: 12pt
- Line spacing: Single
- Margins: 1 inch
- Page markers: HSIRB format

### 4. generate_irb_package.sh

**Purpose:** Full automation - screenshots + IRB generation

**Usage:**
```bash
./scripts/generate_irb_package.sh --config config.json
```

---

## Requirements

### Software
- **Python 3.8+**
- **R 4.0+**
- **Chrome/Chromium** (for Selenium)
- **LaTeX** (XeLaTeX) - for PDF generation
- **Pandoc 2.0+** - for document conversion

### Python Packages
```bash
pip install selenium
```

### R Packages
```R
install.packages(c(
  "rmarkdown",
  "knitr"
))
```

### System Packages
```bash
# macOS
brew install pandoc
brew install --cask basictex  # or mactex for full LaTeX

# Linux (Ubuntu/Debian)
sudo apt-get install pandoc texlive-xetex texlive-fonts-recommended
```

---

## Customization Guide

### For Your Institution

If adapting for another institution:

1. **Update formatting standards:**
   - Edit `configs/nicholls_hsirb_settings.json`
   - Change font, spacing, margins as needed
   - Update page marker format

2. **Modify templates:**
   - Edit `templates/IRB_Application_Template.Rmd`
   - Update header blocks (institution name, IRB office)
   - Adjust procedural preface text
   - Change form field labels

3. **Customize scripts:**
   - Edit `scripts/generate_irb_package.sh`
   - Update default paths and settings

### For Your Project Type

1. **Survey/questionnaire studies:**
   - Use example configs in `configs/`
   - Capture welcome, questions, thank you pages

2. **Experimental studies:**
   - Capture experimental conditions
   - Document randomization process
   - Screenshot stimuli presentation

3. **Interview studies:**
   - Template for interview protocols
   - Recruitment script screenshots

---

## Best Practices

### Screenshots
- ✓ Capture at consistent resolution (1400x900 or 1400x1100)
- ✓ Use descriptive filenames (01_welcome, 02_consent, etc.)
- ✓ Include all key user-facing screens
- ✓ Show data collection methods clearly
- ✓ Capture informed consent language

### IRB Documents
- ✓ Use templates as starting point
- ✓ Fill all form fields completely
- ✓ Be specific about population and procedures
- ✓ Include all required appendices
- ✓ Verify formatting before submission

### Automation
- ✓ Test scripts with sample data first
- ✓ Keep configs in version control
- ✓ Document any customizations
- ✓ Maintain separate configs per project

---

## Troubleshooting

### Screenshots Not Capturing
```bash
# Check if server is running
curl http://localhost:8080

# Test Chrome driver
python3 -c "from selenium import webdriver; webdriver.Chrome()"

# Check output directory permissions
ls -la screenshots/
```

### PDF Generation Fails
```bash
# Verify R packages
R -e "library(rmarkdown); library(knitr)"

# Check XeLaTeX
which xelatex

# Test with minimal Rmd
R -e "rmarkdown::render('test.Rmd', output_format = 'pdf_document')"
```

### Formatting Issues
- **Wrong font:** Ensure Times New Roman is installed on system
- **Page markers missing:** Check YAML header includes fancyhdr settings
- **Images not embedding:** Verify relative paths in Rmd are correct

---

## Examples

See `examples/conjoint_analysis_example/` for a complete working example with:
- Web application (HTML/CSS/JS)
- Screenshot config
- Customized IRB template
- Generated outputs (PDF, Word, screenshots)

---

## Support

**For questions or issues:**
- Check documentation in `docs/` folder
- Review example configs in `configs/`
- See complete example in `examples/`

**For Nicholls-specific guidance:**
- Read `docs/NICHOLLS_IRB_GUIDE.md`
- Contact HSIRB office: irb@nicholls.edu, (985) 448-4171

---

## License

This toolkit is provided as-is for academic research purposes.

Adapt and modify as needed for your institution and projects.

---

## Version History

**v1.0 (October 2025)**
- Initial release
- Nicholls HSIRB formatting support
- Screenshot automation tools
- Complete IRB application templates
- Verification scripts

---

**Created by:** Cursor AI Assistant  
**Based on:** Conjoint Analysis Classroom Exercise IRB Application  
**Institution:** Nicholls State University  
**Date:** October 2025

