# Active Studies in SONA System

**Last Updated**: October 17, 2025

---

## Study 1: EI Pilot (Demo/Testing)

**Purpose**: Demonstration and testing study  
**Slug**: `ei-pilot`  
**Status**: Demo with test data

### Details
- **IRB Status**: Not Required (pilot testing)
- **Protocol**: Placeholder template with test submission form
- **Monitoring**: Enabled (min N=20, BF threshold=10)
- **Test Data**: 40 responses, BF=12.0 (notification triggered)

### URLs
- Protocol: http://localhost:8000/studies/ei-pilot/run/
- Status: http://localhost:8000/studies/ei-pilot/status/

### Purpose
Use this study to:
- Test the SONA system functionality
- Verify monitoring and notifications work
- Demonstrate the dashboard features
- Train yourself on the system before launching real studies

---

## Study 2: EI × Dunning–Kruger Study

**Purpose**: Research study examining DK effects in EI self-assessment  
**Slug**: `ei-dk`  
**Status**: ✅ READY FOR PILOT LAUNCH

### Details
- **Title**: EI × Dunning–Kruger Study
- **IRB Status**: Not Required (pilot testing)
- **Protocol**: Sheldon et al. (2014) replication
- **Monitoring**: Enabled (min N=20, BF threshold=10)
- **Analysis**: Placeholder (needs custom DK correlation BF)

### Study Flow (7 Phases)
1. Consent - Educational pilot disclosure
2. Demographics - Optional background (age, gender, status)
3. Self-Estimates - Pre-test percentile estimates (overall + 4 domains)
4. EI Test - 36 video-based items across 3 workplace scenarios
5. Feedback - Immediate percentile feedback with radar charts
6. Outcomes - Interest, likelihood, WTP for EI training
7. Debrief - DK explanation and resources

### Assets
- **Item Bank**: 36 items across 3 videos
- **Videos**: 
  - Video 1: Feedback delivery (8.9 MB)
  - Video 2: Deadline stress (6.9 MB)
  - Video 3: Colleague support (6.5 MB)
- **Total Size**: ~24 MB

### URLs
- **Protocol**: http://localhost:8000/studies/ei-dk/run/
- **Status**: http://localhost:8000/studies/ei-dk/status/
- **API**: http://localhost:8000/api/studies/95bc0b80-af71-4221-a7ac-72c6bbe20fb9/submit/

### Data Collected
Each participant submission includes:
- Demographics (optional)
- Self-estimates (5 domains, pre-test)
- Test responses (36 items)
- Test scores (overall + 4 domains)
- Actual percentiles (Bayesian estimates)
- **Bias metrics** (self - actual) - KEY for DK analysis
- Outcomes (interest, likelihood, WTP)
- Timing metadata

### Key DK Metrics
- **Calibration**: r(actual, self-estimate)
- **Bias (DK)**: r(actual, self - actual) → Expect r < -0.2
- **Absolute Error**: r(actual, |bias|)
- **Outcomes**: Correlations with ability and bias

### Expected Patterns (Sheldon et al. 2014)
- Mean self-estimate: ~70-77th percentile
- Mean actual: ~40-50th percentile
- Calibration r: 0.09-0.23 (weak)
- Bias r: -0.40 to -0.80 (DK pattern)
- Interest × Actual: Negative (low performers more interested)

### Duration
20-25 minutes per participant

---

## Researcher Dashboard

**All Studies**: http://localhost:8000/studies/researcher/

### Login Credentials
- **Email**: researcher@example.com
- **Password**: demo123

---

## Quick Commands

### Check Response Count
```bash
python manage.py shell -c "
from apps.studies.models import Study
for s in Study.objects.all():
    print(f'{s.slug}: N={s.response_count}, BF={s.current_bf}')
"
```

### Manually Trigger Monitoring
```bash
python manage.py shell -c "
from apps.studies.tasks import run_sequential_bayes_monitoring
from apps.studies.models import Study
study = Study.objects.get(slug='ei-dk')
result = run_sequential_bayes_monitoring(str(study.id))
print(result)
"
```

### View Recent Responses
```bash
python manage.py shell -c "
from apps.studies.models import Response
for r in Response.objects.order_by('-created_at')[:5]:
    print(f'{r.study.slug}: {r.created_at}')
"
```

---

## Next Steps

### For EI × DK Study

1. **Test the protocol**: Complete it yourself at http://localhost:8000/studies/ei-dk/run/
2. **Verify data submission**: Check admin for Response record
3. **Pilot test**: Run with 2-3 participants
4. **Launch**: Share URL when ready
5. **Monitor**: Watch status dashboard as N grows
6. **Replace placeholder**: Create real Bayesian DK correlation analysis when ready

### When N ≥ 20

The monitoring system will:
- Compute BF using the analysis plugin
- Update the status dashboard
- Send notification when BF ≥ 10
- Continue monitoring until you disable it

### To Add Real Analysis

Create: `apps/studies/analysis/ei_dk_analysis.py`

```python
def compute_bf(responses, params):
    """Compute BF for DK correlation pattern"""
    import numpy as np
    from scipy import stats
    
    actual = [r['actualPercentiles']['overall']['point'] for r in responses]
    bias = [r['biasMetrics']['overall']['bias'] for r in responses]
    
    r_val, p_val = stats.pearsonr(actual, bias)
    
    # Compute directional BF (H1: r < -0.2)
    # Use BayesFactor package or custom implementation
    
    # Placeholder logic:
    if r_val < -0.5:
        return 15.0  # Strong DK evidence
    elif r_val < -0.2:
        return 5.0   # Moderate DK evidence
    else:
        return 0.5   # Weak/no DK evidence
    
    return bf
```

Then update study in admin to use:  
`apps.studies.analysis.ei_dk_analysis:compute_bf`

---

## Documentation

- **EI × DK Ready**: `EI_DK_STUDY_READY.md`
- **Protocol Integration**: `PROTOCOL_INTEGRATION_GUIDE.md`
- **Bayesian Monitoring**: `BAYESIAN_MONITORING_GUIDE.md`
- **Quick Start**: `EI_PILOT_QUICK_START.md`
- **Protocols List**: `PROTOCOLS_INTEGRATED.md`

---

**Your SONA system is ready for pilot data collection!** 🚀

Open http://localhost:8000/studies/ei-dk/run/ and start testing!

