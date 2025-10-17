# Conjoint Analysis Example

**Complete working example of IRB automation for a conjoint analysis classroom exercise**

---

## Overview

This example demonstrates the complete IRB automation workflow for a web-based research study.

**Study Type:** Educational classroom exercise using conjoint analysis  
**IRB Category:** Expedited Review (Category 7)  
**Population:** Undergraduate students in Labor Economics course  
**Data Collection:** Anonymous web-based survey

---

## Files Included

### Web Application
- `student_survey.html` - Student-facing survey application
- `instructor_dashboard.html` - Instructor analysis dashboard
- `choice_task_sample.html` - Standalone choice task for screenshots

### Screenshots (5 total)
- `01_welcome_page.png` - Welcome page with consent
- `02_anonymity_notice.png` - Instructions and anonymity assurance
- `03_choice_task_options_A_and_B.png` - Core data collection (choice task)
- `04_instructor_dashboard.png` - Dashboard landing page
- `05_instructor_dashboard_charts.png` - Analysis visualization

### Configuration
- `config.json` - Screenshot capture configuration
- `irb_settings.json` - Study-specific IRB settings

---

## How This Was Generated

### Step 1: Configure Screenshots
```json
{
  "screenshots": [
    {
      "name": "01_welcome_page",
      "path": "/student_survey.html",
      "viewport": {"width": 1400, "height": 900},
      "scroll": 0,
      "wait_seconds": 3
    },
    ...
  ]
}
```

### Step 2: Capture Screenshots
```bash
# Start server
python3 -m http.server 8080 &

# Capture all screenshots
python3 ../../scripts/capture_screenshots.py --config config.json

# Stop server
pkill -f "python3 -m http.server 8080"
```

### Step 3: Customize IRB Template
- Copied `IRB_Application_Template.Rmd`
- Updated PI information (Dr. Martin Meder)
- Described 8-phase exercise
- Added 9 assessment items
- Embedded screenshots in Appendix E

### Step 4: Generate Documents
```bash
R -e "rmarkdown::render('My_IRB_Application.Rmd', output_format = 'all')"
```

**Output:**
- PDF (542 KB, 22 pages) with embedded screenshots
- Word document (406 KB) for editing

---

## Study Details

### Exercise Structure
1. Welcome & Consent
2. Scenario Context (role-play as employees)
3. Baseline Package Display ($64K compensation)
4. 8 Choice Tasks ($59K packages with trade-offs)
5. Retention Probability Questions
6. Group Work Phase
7. Final Choice Round
8. Assessment Questions (9 items)

### Compensation Components
1. Base Salary ($37.5K-$42.5K)
2. Annual Raises
3. Health Insurance
4. Retirement Match
5. PTO Days
6. Tuition Reimbursement
7. Professional Certifications
8. Flexibility/Lifestyle Benefits
9. Managerial Training

**Baseline:** $64K total  
**All Options:** $59K total (5K reduction)

---

## IRB Application Highlights

### Population
- Undergraduate students in Dr. Meder's Labor Economics course
- Age 18+, voluntary participation
- Educational exercise only (not general recruitment)

### Procedures
- Anonymous web-based survey
- Hypothetical decision-making
- No sensitive information collected
- Minimal risk

### Data Collection
- Static HTML/CSS/JavaScript application
- Data stored locally in browser only
- No server transmission
- Completely anonymous

### Assessment
- 9-item evaluation (Moryl 2013 adaptations)
- Measures educational effectiveness
- Likert scales (1-5)
- Optional open-ended comments

---

## Automation Benefits

### Before Automation
- Manual screenshots (30+ minutes)
- Copy-paste into Word (error-prone)
- Format PDF manually (time-consuming)
- Verify formatting (tedious)

### With Automation
- Automated screenshots (2 minutes)
- Auto-embedded in template
- Perfect formatting guaranteed
- One command generates everything

**Time Saved:** ~2 hours per IRB application

---

## Using This Example

### As a Template
1. Copy this example directory
2. Replace HTML files with your application
3. Update `config.json` with your URLs
4. Customize IRB template with your study details
5. Run automation scripts

### Learning from It
- Review `config.json` to understand screenshot capture
- Study HTML files to see good practices
- Examine IRB template structure
- See how screenshots integrate into PDF

---

## Key Takeaways

### Screenshot Best Practices
✓ Capture all user-facing screens  
✓ Show informed consent clearly  
✓ Document data collection method  
✓ Include key interface elements  
✓ Use consistent resolution (1400x900+)

### IRB Application Best Practices
✓ Be specific about procedures  
✓ Address all risks (even if minimal)  
✓ Explain educational justification  
✓ Document anonymity protections  
✓ Include complete appendices

### Automation Best Practices
✓ Use JSON configs for flexibility  
✓ Make scripts reusable  
✓ Document everything  
✓ Test on example before production  
✓ Version control your configs

---

## Results

**Final IRB Package:**
- ✅ 22-page PDF with embedded screenshots
- ✅ Professional Nicholls HSIRB formatting
- ✅ Complete appendices (A-E)
- ✅ Ready for immediate submission
- ✅ Generated in <5 minutes

**IRB Status:** Approved for expedited review

---

## Reproduce This Example

```bash
# 1. Copy example
cp -r examples/conjoint_analysis_example my_test

# 2. Start server
cd my_test
python3 -m http.server 8080 &

# 3. Run automation
cd ..
./scripts/generate_irb_package.sh \
  --config my_test/config.json \
  --app-dir my_test \
  --output-dir my_test/output

# 4. Check results
open my_test/output/IRB_Application_Template.pdf
```

---

**This example demonstrates the complete IRB automation workflow from start to finish.**

