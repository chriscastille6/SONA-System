# Integrated Protocols Summary

## Successfully Integrated Studies

### 1. EI Pilot (Demo/Test Study)
- **Slug**: `ei-pilot`
- **Status**: Demo study with 40 test responses
- **Protocol**: Placeholder template (for development/testing)
- **IRB Status**: Not Required (pilot testing)
- **Monitoring**: Enabled (min N=20, BF threshold=10)
- **URLs**:
  - Protocol: http://localhost:8000/studies/ei-pilot/run/
  - Status: http://localhost:8000/studies/ei-pilot/status/
- **Test Results**: ✅ BF reached 12.0, notification triggered

### 2. Emotional Intelligence Assessment - Computer Adaptive Test
- **Slug**: `ei-cat`
- **Status**: Ready for pilot launch
- **Protocol**: Comprehensive CAT assessment with 289 items
- **Source**: `Psychological Assessments/emotional-intelligence-assessment/comprehensive-cat-assessment.html`
- **Features**:
  - Multi-domain assessment (self-awareness, self-management, social awareness, relationship management)
  - Computer-adaptive testing (CAT) with item selection
  - Item bank: 289 GPT-generated EI items
  - Validation analysis capabilities
  - Item culling options
- **IRB Status**: Not Required (still in development)
- **Monitoring**: Enabled (min N=20, BF threshold=10)
- **Files Copied**:
  - `comprehensive-cat-assessment.html` → `index.html`
  - `comprehensive-cat-engine.js`
  - `cat-engine.js`
  - `validation-analysis.js`
  - `comprehensive_item_bank.json`
- **URLs**:
  - Protocol: http://localhost:8000/studies/ei-cat/run/
  - Status: http://localhost:8000/studies/ei-cat/status/
  - API: http://localhost:8000/api/studies/85df24e9-26ca-4749-bce0-b734a97cc6db/submit/
- **Integration Status**: ✅ Files copied, Django template variables added
- **Next Step**: Modify `completeAssessment()` function to submit to SONA API

### 3. Employee Preference Assessment - Conjoint Analysis
- **Slug**: `conjoint-analysis`
- **Status**: Ready for classroom use
- **Protocol**: Interactive conjoint analysis exercise
- **Source**: `Website/cnjoint analysis/student_survey.html`
- **Features**:
  - Interactive choice tasks with multiple job attributes
  - Employee preference assessment
  - Salary, benefits, work flexibility, development opportunities
  - Designed for classroom teaching
- **IRB Status**: Exempt (HSIRB-2025-001)
- **IRB Expiration**: 2026-10-17
- **IRB Materials Available**: Yes (in `Website/cnjoint analysis/IRB files/`)
- **Monitoring**: Enabled (min N=30, BF threshold=10)
- **Files Copied**:
  - `student_survey.html` → `index.html`
- **URLs**:
  - Protocol: http://localhost:8000/studies/conjoint-analysis/run/
  - Status: http://localhost:8000/studies/conjoint-analysis/status/
  - API: http://localhost:8000/api/studies/b5ec54b7-d39b-4219-8dde-2b5295bda838/submit/
- **Integration Status**: ✅ Files copied, Django template variables added, IRB info configured
- **Next Step**: Modify submission function to POST to SONA API

## Quick Access Dashboard

All studies visible at: http://localhost:8000/studies/researcher/

Login credentials:
- Email: `researcher@example.com`
- Password: `demo123`

## Integration Locations

### Template Structure
```
templates/projects/
├── ei-pilot/
│   └── protocol/
│       └── index.html (placeholder)
├── ei-cat/
│   └── protocol/
│       ├── index.html
│       ├── comprehensive-cat-engine.js
│       ├── cat-engine.js
│       ├── validation-analysis.js
│       └── comprehensive_item_bank.json
└── conjoint-analysis/
    └── protocol/
        └── index.html
```

## Next Steps for Each Protocol

### EI CAT Assessment
1. Find the `completeAssessment()` function in the HTML
2. Add SONA API submission:
```javascript
async function completeAssessment() {
    const results = catEngine.exportAssessmentResults();
    
    // Submit to SONA
    try {
        const response = await fetch(`/api/studies/${STUDY_ID}/submit/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                assessment_type: 'ei_cat',
                results: results,
                completed_at: new Date().toISOString()
            })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('Submitted to SONA:', data.response_id);
        }
    } catch (error) {
        console.error('Submission error:', error);
    }
    
    // Store for feedback page
    sessionStorage.setItem('comprehensiveCatResults', JSON.stringify(results));
    
    // Redirect to feedback (or show thank you)
    // window.location.href = 'feedback-display.html';
    showThankYouMessage();
}
```

### Conjoint Analysis
1. Find where participant data is collected/submitted
2. Add SONA API submission similar to above
3. Test with a few participants

## Testing Checklist

For each protocol:
- [ ] Load protocol page (check for JS errors)
- [ ] Complete assessment as test participant
- [ ] Verify data submitted to `/api/studies/{id}/submit/`
- [ ] Check Response created in admin: http://localhost:8000/admin/studies/response/
- [ ] View status dashboard showing N increasing
- [ ] Verify BF updates when N ≥ min_sample_size

## Documentation References

- **Integration Guide**: `PROTOCOL_INTEGRATION_GUIDE.md`
- **Monitoring Guide**: `BAYESIAN_MONITORING_GUIDE.md`
- **Quick Start**: `EI_PILOT_QUICK_START.md`
- **Implementation Details**: `EI_PILOT_IMPLEMENTATION_SUMMARY.md`

## IRB Documentation

### Conjoint Analysis IRB Materials
Located at: `/Users/ccastille/Documents/GitHub/Website/cnjoint analysis/IRB files/`

Key files:
- `Conjoint_Analysis_Classroom_Exercise_IRB_Application.pdf`
- `IRB_Screenshots_Appendix_WITH_IMAGES.html`
- `Nicholls IRB Submission.pdf`

**IRB Details in SONA**:
- Status: Exempt
- Number: HSIRB-2025-001
- Expires: 2026-10-17

### EI Assessment IRB
- Status: Not Required (pilot/development phase)
- Will need IRB approval before full research launch

## System Status

✅ **Ready for Pilot Testing**
- Database models created and migrated
- API endpoints functional
- Monitoring system tested and working
- Three protocols integrated
- Researcher dashboard operational
- Status dashboards available

## Command Reference

### View all studies
```bash
python manage.py shell -c "
from apps.studies.models import Study
for s in Study.objects.all():
    print(f'{s.slug}: {s.title} (N={s.response_count})')
"
```

### Check response count
```bash
python manage.py shell -c "
from apps.studies.models import Study
study = Study.objects.get(slug='ei-cat')
print(f'Responses: {study.response_count}')
"
```

### Manually trigger monitoring
```bash
python manage.py shell -c "
from apps.studies.tasks import run_sequential_bayes_monitoring
from apps.studies.models import Study
study = Study.objects.get(slug='ei-cat')
result = run_sequential_bayes_monitoring(str(study.id))
print(result)
"
```

## Access URLs Summary

| Study | Protocol URL | Status Dashboard |
|-------|-------------|------------------|
| EI Pilot | http://localhost:8000/studies/ei-pilot/run/ | http://localhost:8000/studies/ei-pilot/status/ |
| EI CAT | http://localhost:8000/studies/ei-cat/run/ | http://localhost:8000/studies/ei-cat/status/ |
| Conjoint Analysis | http://localhost:8000/studies/conjoint-analysis/run/ | http://localhost:8000/studies/conjoint-analysis/status/ |

**Researcher Dashboard**: http://localhost:8000/studies/researcher/

---

Last Updated: October 17, 2025
Server Running: ✅ http://localhost:8000

