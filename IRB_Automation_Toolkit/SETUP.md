# IRB Automation Toolkit - Setup Guide

**Quick setup guide for the IRB Automation Toolkit**

---

## Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   python3 --version
   ```

2. **R 4.0+**
   ```bash
   R --version
   ```

3. **Chrome/Chromium Browser**
   - For Selenium screenshot automation
   - Chrome Driver will be installed automatically with Selenium

4. **LaTeX (XeLaTeX)**
   ```bash
   # macOS
   brew install --cask basictex
   # or for full LaTeX: brew install --cask mactex
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install texlive-xetex texlive-fonts-recommended
   
   # Verify installation
   xelatex --version
   ```

5. **Pandoc 2.0+**
   ```bash
   # macOS
   brew install pandoc
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install pandoc
   
   # Verify installation
   pandoc --version
   ```

---

## Installation Steps

### 1. Install Python Dependencies

```bash
cd IRB_Automation_Toolkit
pip3 install selenium
```

### 2. Install R Packages

```bash
R -e "install.packages(c('rmarkdown', 'knitr'), repos='https://cran.r-project.org')"
```

### 3. Verify Installation

```bash
# Test Python setup
python3 -c "import selenium; print('Selenium:', selenium.__version__)"

# Test R setup
R -e "library(rmarkdown); library(knitr); print('R packages OK')"

# Test LaTeX
xelatex --version | head -1

# Test Pandoc
pandoc --version | head -1
```

---

## Quick Test

### Test Screenshot Capture

```bash
# Start a simple web server
cd examples/
python3 -m http.server 8080 &

# Capture a screenshot
cd ..
python3 scripts/capture_screenshots.py \
  --url http://localhost:8080 \
  --output test_screenshots/

# Stop server
pkill -f "python3 -m http.server 8080"

# Check output
ls -lh test_screenshots/
```

### Test IRB Document Generation

```bash
cd templates/

# Generate PDF
R -e "rmarkdown::render('IRB_Exempt_Template.Rmd', output_format = rmarkdown::pdf_document(latex_engine = 'xelatex'))"

# Check output
ls -lh IRB_Exempt_Template.pdf
```

---

## Configuration

### 1. Copy Example Config

```bash
cp configs/example_config.json configs/my_project_config.json
```

### 2. Edit Configuration

Edit `configs/my_project_config.json`:

```json
{
  "project": {
    "name": "My Research Project",
    "pi_name": "Dr. Your Name",
    "pi_phone": "985-448-XXXX",
    "pi_email": "your.email@nicholls.edu"
  },
  "server": {
    "url": "http://localhost:8080",
    "directory": "/path/to/your/app",
    "port": 8080
  },
  "screenshots": [
    ...
  ]
}
```

### 3. Customize IRB Template

```bash
cd templates/
cp IRB_Application_Template.Rmd My_Project_IRB.Rmd
# Edit My_Project_IRB.Rmd with your study details
```

---

## Troubleshooting

### Python/Selenium Issues

**Problem:** Selenium not found
```bash
pip3 install --upgrade selenium
```

**Problem:** Chrome driver issues
```bash
# Chrome driver installs automatically with Selenium 4+
# If issues persist, manually install:
brew install chromedriver  # macOS
```

### R/Markdown Issues

**Problem:** rmarkdown package not found
```bash
R -e "install.packages('rmarkdown', repos='https://cran.r-project.org')"
```

**Problem:** LaTeX errors
```bash
# Install additional LaTeX packages
sudo tlmgr install collection-fontsrecommended
sudo tlmgr install collection-latexextra
```

### Pandoc Issues

**Problem:** Pandoc not found
```bash
# macOS
brew install pandoc

# Linux
sudo apt-get update && sudo apt-get install pandoc
```

**Problem:** Old pandoc version
```bash
# Update pandoc
brew upgrade pandoc  # macOS
```

---

## Directory Setup

```bash
# Create your project structure
mkdir -p my_irb_project/{app,screenshots,output}

# Copy toolkit
cp -r IRB_Automation_Toolkit my_irb_project/toolkit

# Copy config
cp toolkit/configs/example_config.json my_irb_project/config.json

# Edit paths in config.json to match your setup
```

---

## Next Steps

1. **Review examples:** `cd examples/conjoint_analysis_example/`
2. **Read documentation:** `cd docs/` and review guides
3. **Customize templates:** Edit files in `templates/`
4. **Test full workflow:** Run `scripts/generate_irb_package.sh`

---

## Platform-Specific Notes

### macOS
- Use Homebrew for most installations
- May need to allow Chrome driver in Security & Privacy settings
- XeLaTeX included in BasicTeX or MacTeX

### Linux (Ubuntu/Debian)
- Use apt-get for system packages
- May need to install Chrome manually for Selenium
- texlive-xetex provides XeLaTeX

### Windows
- Install Python from python.org
- Install R from r-project.org
- Install MiKTeX for LaTeX
- Install Pandoc from GitHub releases
- Use WSL for shell scripts or adapt to PowerShell

---

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Selenium package installed
- [ ] R 4.0+ installed
- [ ] rmarkdown and knitr packages installed
- [ ] XeLaTeX installed and working
- [ ] Pandoc 2.0+ installed
- [ ] Chrome/Chromium browser available
- [ ] Scripts are executable (`chmod +x scripts/*.py scripts/*.sh`)
- [ ] Test screenshot capture works
- [ ] Test PDF generation works

---

## Getting Help

**Documentation:**
- `README.md` - Main overview
- `docs/NICHOLLS_IRB_GUIDE.md` - IRB process guide
- `docs/SCREENSHOT_GUIDE.md` - Screenshot best practices

**Examples:**
- `examples/conjoint_analysis_example/` - Complete working example

**Issues:**
- Check troubleshooting section above
- Review error messages carefully
- Ensure all prerequisites are installed

---

**Setup Time:** ~15-30 minutes (depending on what's already installed)

**Ready to start?** Go to README.md for usage instructions!

