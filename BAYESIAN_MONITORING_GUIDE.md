# Bayesian Sequential Monitoring - User Guide

## Overview

The SONA system now supports sequential Bayesian monitoring for research studies. This feature allows you to:

1. Collect protocol responses from participants
2. Automatically compute Bayes Factors as data accumulates
3. Get notified when evidence reaches a threshold (e.g., BF > 10)
4. Track IRB status and OSF project integration

## Quick Start

### 1. Create or Configure a Study

In Django admin or via the researcher dashboard:

- Set **Monitoring Enabled** to `True`
- Set **Minimum Sample Size** (default: 20) - monitoring starts after this N
- Set **BF Threshold** (default: 10.0) - you'll be notified when BF ≥ this value
- Set **Analysis Plugin** to your Bayesian analysis function (default: placeholder)

### 2. IRB Configuration

- **IRB Status**: `not_required`, `approved`, `exempt`, `pending`, or `expired`
- **IRB Number**: Your protocol number
- **IRB Expiration**: Date when approval expires

### 3. OSF Configuration (Optional)

- **OSF Enabled**: Check if project is on Open Science Framework
- **OSF Project ID**: Your OSF project identifier
- **OSF Link**: Full URL to OSF project

### 4. Protocol Integration

#### Option A: Project-Specific HTML Protocol

Place your protocol HTML at:
```
templates/projects/{study-slug}/protocol/index.html
```

Static assets go in:
```
static/projects/{study-slug}/
```

The protocol should POST responses to:
```javascript
fetch('/api/studies/{study-id}/submit/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        // your response data
        response: "answer",
        score: 42,
        // ... etc
    })
})
```

#### Option B: Use Placeholder for Testing

Visit `/studies/{study-slug}/run/` and the system will show a placeholder with a test submission form.

### 5. Monitoring Flow

1. **Data Collection**: Participants complete protocol → responses saved
2. **Threshold Check**: After N ≥ `min_sample_size`, monitoring begins
3. **BF Computation**: On each new response, the analysis plugin computes BF
4. **Notification**: When BF ≥ `bf_threshold`, you receive an email/notification
5. **Dashboard**: View real-time status at `/studies/{study-slug}/status/`

## Analysis Plugin Interface

### Default Placeholder

The system includes a placeholder that returns dummy BF values:
- N < 20: BF = 0.5 (weak evidence for H0)
- N = 20-29: BF = 3.0 (anecdotal evidence for H1)
- N = 30-39: BF = 8.0 (moderate evidence for H1)
- N ≥ 40: BF = 12.0 (strong evidence for H1, triggers notification)

### Custom Analysis Plugin

Create your own analysis function:

```python
# apps/studies/analysis/my_analysis.py
from typing import Dict, Any, Sequence

def compute_bf(responses: Sequence[Dict[str, Any]], params: Dict[str, Any]) -> float:
    """
    Compute Bayes Factor BF10.
    
    Args:
        responses: List of Response.payload dicts
        params: Optional configuration (not currently used)
    
    Returns:
        Bayes Factor BF10 (H1/H0)
    """
    # Example: two-group Bayesian t-test
    import numpy as np
    from scipy import stats
    
    # Extract data from responses
    group_a = [r['score'] for r in responses if r.get('group') == 'A']
    group_b = [r['score'] for r in responses if r.get('group') == 'B']
    
    # Compute BF using your preferred method
    # (e.g., BayesFactor R package via rpy2, PyMC, custom implementation)
    
    # Dummy example:
    t_stat, p_value = stats.ttest_ind(group_a, group_b)
    bf = compute_bf_from_t(t_stat, len(group_a), len(group_b))
    
    return bf
```

Then update Study's `analysis_plugin` field:
```
apps.studies.analysis.my_analysis:compute_bf
```

## Management Commands

### Create EI Pilot Demo

```bash
python manage.py create_ei_pilot
```

This creates a demo study configured for pilot testing.

## Celery Tasks

The monitoring runs via Celery background tasks:

- **`run_sequential_bayes_monitoring(study_id)`**: Computes BF and checks threshold
- **`send_bf_notification(study_id)`**: Sends email when threshold reached

To trigger manually:
```python
from apps.studies.tasks import run_sequential_bayes_monitoring
run_sequential_bayes_monitoring.delay(str(study_id))
```

## Dashboard Views

### Researcher Dashboard
`/studies/researcher/`

Shows all your studies with:
- Response count
- Current BF (if computed)
- Monitoring status
- IRB status badges

### Study Status Dashboard
`/studies/{slug}/status/`

Detailed view showing:
- IRB and OSF status
- N, min sample size, monitoring state
- Current BF vs threshold
- Recent responses preview
- Notification status

## API Endpoints

### Submit Response
```
POST /api/studies/{study-id}/submit/
Content-Type: application/json

{
  "response": "data",
  "score": 42,
  ...
}
```

Returns:
```json
{
  "success": true,
  "response_id": "uuid",
  "session_id": "uuid"
}
```

### Run Protocol
```
GET /studies/{slug}/run/
```

Serves project-specific protocol HTML or placeholder.

### View Status
```
GET /studies/{slug}/status/
```

Status dashboard for researchers.

## Example: EI Pilot Workflow

1. **Setup Study**
   ```bash
   python manage.py create_ei_pilot
   ```

2. **Install Protocol HTML** (when ready)
   ```
   templates/projects/ei-pilot/protocol/index.html
   ```

3. **Share Protocol URL**
   ```
   https://yourdomain.com/studies/ei-pilot/run/
   ```

4. **Monitor Progress**
   - Visit: `https://yourdomain.com/studies/ei-pilot/status/`
   - Watch N accumulate
   - After N ≥ 20, BF updates on each submission

5. **Replace Placeholder Analysis**
   - Create your PyMC/BayesFactor model
   - Update `analysis_plugin` in admin
   - Monitoring continues with real BF

6. **Receive Notification**
   - When BF ≥ 10, email sent
   - Dashboard shows "Hypothesis Supported!"

## Future Enhancements

- Auto-export to OSF when threshold reached
- IRB renewal reminders (email when expiration approaching)
- Richer visualizations (BF over time, sequential evidence plots)
- CSV/Parquet data export endpoints
- Multi-hypothesis monitoring (multiple BF thresholds)

## Troubleshooting

**Q: BF not updating?**
- Check that `monitoring_enabled = True`
- Verify N ≥ `min_sample_size`
- Check Celery is running: `celery -A config worker -l info`
- Manually trigger: `run_sequential_bayes_monitoring.delay(study_id)`

**Q: No notification email?**
- Ensure `EMAIL_HOST` configured in settings
- Check `monitoring_notified` flag hasn't already been set
- Notification shows in dashboard even without email

**Q: Protocol not loading?**
- Verify template path: `templates/projects/{slug}/protocol/index.html`
- Check slug matches study slug exactly
- Placeholder will show if template not found

**Q: Analysis plugin error?**
- Check Python import path syntax: `module.path:function_name`
- Verify function signature matches: `compute_bf(responses, params) -> float`
- Check server logs for import errors

## Support

For questions or issues, contact the system administrator or refer to the Django admin documentation.


