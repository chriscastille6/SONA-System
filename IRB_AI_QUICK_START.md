# AI-Assisted IRB Review - Quick Start Guide

**Get started in 5 minutes!**

---

## Step 1: Configure API Key (Optional for Testing)

The system works without an API key (returns placeholder results). To use real AI analysis:

```bash
# Add to your .env file or export:
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Get an API key at: https://console.anthropic.com/

---

## Step 2: Access the System

### For Researchers

**Login**: http://localhost:8002/accounts/login/
- Email: `researcher@example.com`
- Password: `demo123`

**Your Dashboard**: http://localhost:8002/studies/researcher/

### For Committee Members

**Committee Dashboard**: http://localhost:8002/studies/committee/
- Requires staff/admin account

---

## Step 3: Run Your First Review

### Option A: Test Command (Fastest)

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py test_irb_review
```

This creates a test review for the EI × DK study and runs it immediately.

### Option B: Via Web Interface

1. **Go to**: http://localhost:8002/studies/researcher/
2. **Find**: EI × Dunning–Kruger Study
3. **Click**: "AI IRB Review" button
4. **Upload** (Optional):
   - Protocol document (PDF, Word, etc.)
   - Consent form
   - Survey materials
5. **Or Link OSF** (Optional):
   - Enter OSF repository URL
6. **Click**: "Start AI Review"
7. **Wait**: 2-5 minutes (you'll get email when done)
8. **View Report**: Click link in email or go to review history

---

## Step 4: View Results

### What You'll See

**Overall Risk Assessment**:
- ✅ Minimal Risk - No significant concerns
- 🟢 Low Risk - Minor issues
- 🟡 Moderate Risk - Several issues to address
- 🔴 High Risk - Critical issues requiring attention

**Categorized Issues**:
- **Critical** (red) - Must fix before IRB submission
- **Moderate** (yellow) - Should address to strengthen protocol
- **Minor** (gray) - Suggestions and best practices

**For Each Issue**:
- Description of the problem
- Specific recommendation to fix it
- Which document/section is affected
- Which AI agent identified it

---

## Step 5: Respond to Issues

1. **Mark Issues Addressed**: Check boxes for fixed issues
2. **Add Notes**: Explain what you changed
3. **Save Response**: Documents your actions for committee
4. **Re-Review** (Optional): Run new review with updated materials

---

## URLs Cheat Sheet

### Researchers

| Action | URL |
|--------|-----|
| Your studies | http://localhost:8002/studies/researcher/ |
| Create review | http://localhost:8002/studies/{study-id}/irb-review/create/ |
| View report | http://localhost:8002/studies/{study-id}/irb-review/{version}/ |
| Review history | http://localhost:8002/studies/{study-id}/irb-review/history/ |

### Committee

| Action | URL |
|--------|-----|
| Dashboard | http://localhost:8002/studies/committee/ |
| Admin | http://localhost:8002/admin/studies/irbreview/ |

### For EI × DK Study

- **Create Review**: http://localhost:8002/studies/95bc0b80-af71-4221-a7ac-72c6bbe20fb9/irb-review/create/
- **Review History**: http://localhost:8002/studies/95bc0b80-af71-4221-a7ac-72c6bbe20fb9/irb-review/history/

---

## What Gets Analyzed

### The Five Agents Check:

1. **Ethics Agent**:
   - Belmont principles (respect, beneficence, justice)
   - Scientific merit
   - Conflicts of interest
   - Deception and risks

2. **Privacy Agent**:
   - PII collection and minimization
   - De-identification procedures
   - Confidentiality safeguards
   - Data retention and destruction

3. **Vulnerability Agent**:
   - Vulnerable populations involved
   - Special protections needed
   - Coercion and power dynamics
   - Appropriate consent procedures

4. **Data Security Agent**:
   - Encryption (at rest and in transit)
   - Access controls
   - Secure storage and transmission
   - Breach response plans

5. **Consent Agent**:
   - Required consent elements
   - Language clarity and reading level
   - Voluntariness
   - No exculpatory language

---

## Testing Without API Key

If you don't have an Anthropic API key configured:

- System returns **placeholder results**
- Shows one minor issue per agent ("API not configured")
- Demonstrates UI and workflow
- Good for testing the interface

To see real analysis, configure the API key.

---

## Common Issues & Solutions

### "Review status is pending forever"

**Solution**: Celery worker might not be running. The review task runs synchronously if called directly:

```bash
python manage.py shell -c "
from apps.studies.tasks import run_irb_ai_review
from apps.studies.models import IRBReview
review = IRBReview.objects.order_by('-initiated_at').first()
result = run_irb_ai_review(str(review.id))
print(result)
"
```

### "Failed lookup for key [irb_review_status]"

**Solution**: Refresh the page. The property might not have loaded.

### "API key not working"

**Check**:
1. Key starts with `sk-ant-api03-`
2. Key is in environment: `echo $ANTHROPIC_API_KEY`
3. Django can see it: `python manage.py shell -c "from django.conf import settings; print(settings.ANTHROPIC_API_KEY)"`

---

## Next Steps

1. ✅ **Test the system** with the command or web interface
2. ✅ **Review the results** - even placeholder results show the structure
3. ✅ **Configure API key** when ready for real analysis
4. ✅ **Upload real materials** for your EI × DK study
5. ✅ **Iterate** - run multiple reviews as you improve your protocol

---

## Full Documentation

- **User Guide**: `IRB_AI_REVIEW_GUIDE.md` - Complete reference
- **Implementation Summary**: `IRB_AI_IMPLEMENTATION_SUMMARY.md` - Technical details
- **This Guide**: `IRB_AI_QUICK_START.md` - Get started quickly

---

**Ready to improve your research ethics! 🚀**

Start here: http://localhost:8002/studies/researcher/







