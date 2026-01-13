# Protocol Integration Guide

## Quick Integration of Your Assessment Protocols

This guide helps you integrate HTML protocols from your Psychological Assessments folder into the SONA system.

## Available Protocols

From `/Users/ccastille/Documents/GitHub/Psychological Assessments/`:

1. **emotional-intelligence-assessment/**
   - `comprehensive-cat-assessment.html` - Full 289-item adaptive test
   - `cat-assessment.html` - Standard CAT version
   - `static-assessment-form.html` - Simple static form

2. **burnout-assessment/**
   - `demo-olbi-complete.html` - Complete OLBI with outcome prediction
   - `demo-olbi.html` - Standard OLBI
   - `demo-simple.html` - Simplified version

3. **managerial-fit-assessment/**
   - Various HTML files available

## Step 1: Integrate Protocol into SONA

Use the management command to copy files and create the study:

```bash
python manage.py integrate_protocol \
    emotional-intelligence-assessment \
    comprehensive-cat-assessment.html \
    --title "Emotional Intelligence Assessment (CAT)" \
    --slug "ei-cat" \
    --description "Computer-adaptive emotional intelligence assessment" \
    --min-n 20 \
    --bf-threshold 10.0
```

Or for burnout:

```bash
python manage.py integrate_protocol \
    burnout-assessment \
    demo-olbi-complete.html \
    --title "OLBI Burnout Assessment" \
    --slug "burnout-olbi" \
    --description "Oldenburg Burnout Inventory with outcome prediction" \
    --min-n 30 \
    --bf-threshold 10.0
```

This will:
- ✓ Create the study in the database
- ✓ Copy the HTML file to `templates/projects/{slug}/protocol/index.html`
- ✓ Copy related JS/JSON files automatically
- ✓ Set up monitoring with your specified parameters

## Step 2: Modify HTML to Submit Data

After integration, edit the copied HTML file at:
```
templates/projects/{slug}/protocol/index.html
```

### Add Django Template Variables

At the top of your HTML (in a script tag):

```javascript
<script>
    // Django template variables
    const STUDY_ID = '{{ study.id }}';
    const STUDY_SLUG = '{{ study.slug }}';
</script>
```

### Modify Your Submit Function

Find where your HTML collects and submits data. Replace or modify it to:

```javascript
async function submitAssessmentData(responseData) {
    try {
        const response = await fetch(`/api/studies/${STUDY_ID}/submit/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                // Your assessment data
                responses: responseData.responses,
                scores: responseData.scores,
                metadata: {
                    duration_seconds: responseData.duration,
                    completed_at: new Date().toISOString()
                },
                // Include whatever structure your analysis needs
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Data submitted successfully!');
            console.log('Response ID:', result.response_id);
            console.log('Session ID:', result.session_id);
            
            // Show thank you page or redirect
            showThankYouMessage();
        } else {
            console.error('Submission failed:', result.error);
            alert('There was an error submitting your responses. Please contact the researcher.');
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Network error. Please check your connection and try again.');
    }
}
```

### Example for EI CAT Assessment

If your `comprehensive-cat-assessment.html` has a completion function like:

```javascript
function completeAssessment() {
    const results = {
        domain_scores: domainScores,
        all_responses: userResponses,
        // ... etc
    };
    displayResults(results);
}
```

Modify it to:

```javascript
async function completeAssessment() {
    const results = {
        domain_scores: domainScores,
        all_responses: userResponses,
        items_administered: itemsAdministered,
        // ... etc
    };
    
    // Submit to SONA
    await submitAssessmentData(results);
    
    // Then show results
    displayResults(results);
}
```

## Step 3: Test the Integration

1. **Start the server** (if not already running):
   ```bash
   python manage.py runserver
   ```

2. **Access the protocol**:
   ```
   http://localhost:8000/studies/{slug}/run/
   ```

3. **Complete the assessment** and verify data submission

4. **Check the status dashboard**:
   ```
   http://localhost:8000/studies/{slug}/status/
   ```

5. **View responses in admin**:
   ```
   http://localhost:8000/admin/studies/response/
   ```

## Step 4: Verify Data Collection

Check that responses are being saved:

```bash
python manage.py shell
```

```python
from apps.studies.models import Study, Response

# Get your study
study = Study.objects.get(slug='ei-cat')

# Check response count
print(f"Responses: {study.response_count}")

# View latest response
latest = study.responses.order_by('-created_at').first()
if latest:
    print(f"Latest response payload: {latest.payload}")
```

## Quick Integration Commands

### EI Assessment (when ready)

```bash
# Full CAT version
python manage.py integrate_protocol \
    emotional-intelligence-assessment \
    comprehensive-cat-assessment.html \
    --title "EI Assessment - Comprehensive CAT" \
    --slug "ei-comprehensive"

# Simpler version for testing
python manage.py integrate_protocol \
    emotional-intelligence-assessment \
    static-assessment-form.html \
    --title "EI Assessment - Static Form" \
    --slug "ei-static"
```

### Burnout Assessment

```bash
# Complete version
python manage.py integrate_protocol \
    burnout-assessment \
    demo-olbi-complete.html \
    --title "Burnout Assessment - OLBI Complete" \
    --slug "burnout-complete"

# Simple version
python manage.py integrate_protocol \
    burnout-assessment \
    demo-simple.html \
    --title "Burnout Assessment - Simple" \
    --slug "burnout-simple"
```

### Managerial Fit Assessment

```bash
# Check what HTML files are available first
ls "/Users/ccastille/Documents/GitHub/Psychological Assessments/managerial-fit-assessment/"*.html
```

## Data Structure Recommendations

Your submitted JSON should include:

```javascript
{
    // Core response data
    "responses": [...],  // Individual item responses
    
    // Computed scores
    "scores": {
        "total": 75.5,
        "domains": {
            "domain1": 80,
            "domain2": 71
        }
    },
    
    // Metadata
    "metadata": {
        "completion_time_seconds": 1234,
        "completed_at": "2025-10-17T10:00:00Z",
        "items_administered": 45,
        "adaptive_algorithm": "cat"
    },
    
    // Any analysis-specific data
    "analysis_data": {
        "theta_estimate": 0.75,
        "se": 0.15,
        // ... whatever your Bayesian analysis needs
    }
}
```

## Troubleshooting

### Protocol doesn't load
- Check file exists: `templates/projects/{slug}/protocol/index.html`
- Check slug matches exactly (no typos)
- Check server logs for template errors

### Data not submitting
- Check browser console for JavaScript errors
- Verify STUDY_ID is set correctly (should be a UUID)
- Check network tab for API response
- Verify CSRF token not blocking (API endpoint is exempt)

### Related files not found (JS/CSS)
- Copy them to the same directory as index.html
- Or update paths in HTML to match new location
- Static files go in: `static/projects/{slug}/`

## Next Steps After Integration

1. **Modify HTML** to submit to SONA API ✓
2. **Test with real users** (or yourself)
3. **Monitor data collection** on status dashboard
4. **When ready**: Replace placeholder analysis with real Bayesian model
5. **Configure IRB** status when approved
6. **Link to OSF** when project registered

## Need Help?

Check these files:
- `BAYESIAN_MONITORING_GUIDE.md` - Complete system documentation
- `EI_PILOT_QUICK_START.md` - Quick reference
- `EI_PILOT_IMPLEMENTATION_SUMMARY.md` - Technical details

Or view existing working example:
- Study: EI Pilot (`ei-pilot`)
- Protocol: `/studies/ei-pilot/run/`
- Status: `/studies/ei-pilot/status/`


