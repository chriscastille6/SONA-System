# EI Pilot Quick Start Guide

## 🚀 System Status: READY FOR PILOT TESTING

The SONA system has been configured for the EI pilot with sequential Bayesian monitoring.

## Quick Access URLs

After starting the server (`python manage.py runserver`):

- **Protocol Page**: http://localhost:8000/studies/ei-pilot/run/
- **Status Dashboard**: http://localhost:8000/studies/ei-pilot/status/
- **Researcher Dashboard**: http://localhost:8000/studies/researcher/
- **Django Admin**: http://localhost:8000/admin/

## Current Configuration

**Study**: EI Pilot - Emotional Intelligence Measurement Protocol
- **Slug**: `ei-pilot`
- **IRB Status**: Not Required (pilot testing)
- **OSF**: Not enabled (placeholder for future)
- **Monitoring**: Enabled
- **Minimum N**: 20 responses before monitoring begins
- **BF Threshold**: 10.0 (notification when BF ≥ 10)
- **Analysis**: Placeholder (returns dummy BF values)

## Next Steps

### Option 1: Use Placeholder for Initial Testing

1. Start server: `python manage.py runserver`
2. Visit: http://localhost:8000/studies/ei-pilot/run/
3. Use the test submission form (researcher view)
4. Watch status update at: http://localhost:8000/studies/ei-pilot/status/

### Option 2: Install Your EI Protocol HTML

1. Create directory:
   ```bash
   mkdir -p templates/projects/ei-pilot/protocol
   ```

2. Add your protocol HTML:
   ```bash
   # Place your HTML file at:
   templates/projects/ei-pilot/protocol/index.html
   ```

3. Configure data submission in your HTML:
   ```javascript
   // In your protocol JavaScript:
   const STUDY_ID = '{{ study.id }}';  // Django template variable
   
   // When participant completes protocol:
   fetch(`/api/studies/${STUDY_ID}/submit/`, {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
           // Your EI measurement data
           ei_score: calculatedScore,
           responses: allResponses,
           // ... etc
       })
   }).then(response => response.json())
     .then(data => {
         console.log('Submitted:', data.response_id);
         // Show thank you page
     });
   ```

4. Refresh protocol page - your HTML will now load automatically!

### Option 3: Replace Analysis Placeholder

When ready to use real Bayesian analysis:

1. Create analysis file:
   ```bash
   nano apps/studies/analysis/ei_analysis.py
   ```

2. Implement compute_bf function:
   ```python
   def compute_bf(responses, params):
       """Compute real Bayes Factor for EI data."""
       # Import your analysis libraries (PyMC, BayesFactor, etc.)
       # Extract data from responses
       # Run Bayesian model
       # Return BF value
       return bf_value
   ```

3. Update study in Django admin:
   - Go to: http://localhost:8000/admin/studies/study/
   - Find EI Pilot study
   - Change `analysis_plugin` to: `apps.studies.analysis.ei_analysis:compute_bf`
   - Save

## Test Data Submission

Quick Python test to submit sample data:

```python
python manage.py shell

# In shell:
from apps.studies.models import Study, Response
from uuid import uuid4

study = Study.objects.get(slug='ei-pilot')

# Submit a test response
Response.objects.create(
    study=study,
    session_id=uuid4(),
    payload={
        'ei_score': 75,
        'test_data': True
    }
)

print(f"Total responses: {study.response_count}")
```

Or via curl:

```bash
# Get study ID first
STUDY_ID=$(python manage.py shell -c "from apps.studies.models import Study; print(Study.objects.get(slug='ei-pilot').id)")

# Submit response
curl -X POST http://localhost:8000/api/studies/$STUDY_ID/submit/ \
  -H "Content-Type: application/json" \
  -d '{"ei_score": 75, "test_data": true}'
```

## Monitoring Workflow

1. **Responses accumulate**: Each submission creates a Response record
2. **Threshold check**: When N ≥ 20, monitoring begins
3. **BF computation**: Placeholder computes BF on each new response
4. **Dashboard updates**: View real-time N and BF at status page
5. **Notification**: When BF ≥ 10, you receive notification (email if configured, otherwise dashboard alert)

### Current Placeholder Logic

The placeholder analysis returns:
- **N < 20**: BF = 0.5 (insufficient data, slight evidence for H0)
- **N = 20-29**: BF = 3.0 (anecdotal evidence for H1)
- **N = 30-39**: BF = 8.0 (moderate evidence for H1)
- **N ≥ 40**: BF = 12.0 (strong evidence for H1) → **Notification sent!**

## Key Management Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Access Django shell
python manage.py shell

# Create superuser (if needed)
python manage.py createsuperuser

# Run migrations (after model changes)
python manage.py makemigrations
python manage.py migrate

# Manually trigger monitoring
python manage.py shell -c "
from apps.studies.tasks import run_sequential_bayes_monitoring
from apps.studies.models import Study
study = Study.objects.get(slug='ei-pilot')
result = run_sequential_bayes_monitoring(str(study.id))
print(result)
"
```

## Troubleshooting

### Protocol page shows placeholder
- Check that `templates/projects/ei-pilot/protocol/index.html` exists
- Verify file path matches slug exactly

### BF not updating
- Ensure `monitoring_enabled = True` in admin
- Check N ≥ `min_sample_size` (default 20)
- Verify responses are being saved (check admin)
- Manually trigger: see management commands above

### No notification received
- Check if `monitoring_notified = True` in admin (already sent)
- Email requires SMTP configuration in settings
- Dashboard notification always shows when BF ≥ threshold

### Cannot access status dashboard
- Must be logged in as researcher or admin
- Check user role in admin panel

## Documentation

📖 **Full guides available:**
- `BAYESIAN_MONITORING_GUIDE.md` - Complete user guide
- `EI_PILOT_IMPLEMENTATION_SUMMARY.md` - Technical details
- `QUICK_ACCESS.md` - General system navigation

## Support

Questions? Check the guides above or:
1. Review Django admin for study configuration
2. Check `logs/django.log` for errors
3. Use `python manage.py shell` to inspect data
4. Refer to implementation summary for architecture details

---

**Ready to launch your EI pilot!** 🎉

Start the server and visit the protocol page to begin data collection.


