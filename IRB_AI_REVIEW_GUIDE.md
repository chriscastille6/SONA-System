# AI-Assisted IRB Review System - User Guide

**Last Updated**: October 22, 2025

---

## Overview

The AI-Assisted IRB Review system provides automated ethical review of research protocols using multiple specialized AI agents. This tool helps researchers identify potential ethical issues before formal IRB submission and assists IRB committees in reviewing protocols more efficiently.

### Key Features

- **Multi-Agent Analysis**: 5 specialized AI agents review different ethical aspects
- **Comprehensive Coverage**: Ethics, privacy, vulnerability, data security, and consent
- **OSF Integration**: Automatically fetch materials from Open Science Framework
- **Version Tracking**: Monitor improvements across multiple review iterations
- **Full Audit Trail**: Complete record of reviews, findings, and responses
- **Committee Dashboard**: IRB committee members can view all reviews

---

## For Researchers

### Starting a Review

1. **Navigate to Your Dashboard**
   - Go to http://localhost:8002/studies/researcher/
   - Find the study you want to review
   - Click "AI IRB Review" button

2. **Provide Materials**
   - **Option A**: Upload documents (protocol, consent form, surveys)
   - **Option B**: Link OSF repository (if study has OSF enabled)
   - **Option C**: Both uploads and OSF

3. **Initiate Review**
   - Click "Start AI Review"
   - Review runs in background (2-5 minutes)
   - You'll receive email notification when complete

### Understanding Results

#### Risk Levels

- **✅ Minimal**: No significant ethical concerns identified
- **🟢 Low**: Minor issues, easily addressed
- **🟡 Moderate**: Several issues requiring attention
- **🔴 High**: Critical issues that may prevent approval

#### Issue Severity

- **Critical**: Must be fixed before IRB submission
- **Moderate**: Should be addressed to strengthen protocol
- **Minor**: Suggestions for best practices

### Responding to Issues

1. **Review Each Finding**
   - Read description and affected section
   - Review the recommendation
   - Plan how to address it

2. **Make Changes**
   - Update your protocol documents
   - Revise consent forms
   - Improve procedures

3. **Document Response**
   - Mark issues as addressed
   - Add notes explaining what you changed
   - Save your response

4. **Re-Review** (Optional)
   - Upload updated materials
   - Run new AI review (creates version 2)
   - Compare results to see improvement

---

## The Five AI Agents

### 1. Ethics Agent
**Focus**: Belmont Report principles

- Respect for persons (autonomy, consent)
- Beneficence (maximize benefits, minimize harms)
- Justice (fair participant selection)
- Scientific merit
- Conflicts of interest

### 2. Privacy Agent
**Focus**: Data protection and confidentiality

- PII collection and minimization
- Data anonymization/de-identification
- Access controls
- Data retention and destruction
- Privacy disclosures

### 3. Vulnerability Agent
**Focus**: Protection of vulnerable populations

- Children, prisoners, pregnant women
- Cognitively impaired individuals
- Students and employees (power dynamics)
- Economically disadvantaged
- Special protections and consent procedures

### 4. Data Security Agent
**Focus**: Technical security measures

- Encryption (at rest and in transit)
- Authentication and access controls
- Secure storage and transmission
- Backup and disaster recovery
- Third-party vendor security
- Breach response plans

### 5. Consent Agent
**Focus**: Informed consent adequacy

- Required elements (risks, benefits, procedures, etc.)
- Language clarity and reading level
- Voluntariness and withdrawal rights
- No exculpatory language
- Comprehension assessment

---

## For IRB Committee Members

### Accessing the Dashboard

1. **Login as Staff/Admin**
   - http://localhost:8002/accounts/login/
   - Must have staff privileges

2. **Committee Dashboard**
   - http://localhost:8002/studies/committee/
   - View all studies with their AI review status
   - Filter by IRB status

### Using AI Reviews in Your Process

#### Pre-Review

- Researchers run AI review before submission
- Committee sees what issues were identified
- Researchers' responses show how issues were addressed
- Reduces back-and-forth on common issues

#### Supplementary Tool

- AI review highlights areas to focus on
- Committee still conducts full human review
- AI may miss nuanced issues requiring expertise
- Use as a screening tool, not replacement

#### Version Tracking

- See improvement across review iterations
- Track which issues were addressed
- Identify persistent concerns

### Triggering Committee Reviews

Committee members can trigger reviews in two ways:

1. **Via Admin Interface**
   - Go to http://localhost:8002/admin/studies/irbreview/
   - Select pending reviews
   - Actions → "Trigger AI review (committee)"

2. **Create New Review**
   - Researchers can create reviews from their dashboard
   - Committee can see results in committee dashboard

---

## Technical Details

### Architecture

**Models**:
- `IRBReview`: Stores review metadata and aggregated results
- `ReviewDocument`: Stores uploaded files with integrity hashes

**AI Agents** (`apps/studies/irb_ai/agents/`):
- `EthicsAgent`
- `PrivacyAgent`
- `VulnerabilityAgent`
- `DataSecurityAgent`
- `ConsentAgent`

**Orchestrator** (`apps/studies/irb_ai/analyzer.py`):
- `IRBAnalyzer`: Coordinates agents, aggregates findings

**Background Processing**:
- Celery task: `run_irb_ai_review`
- Runs asynchronously
- Sends email notifications

### Data Flow

1. Researcher creates `IRBReview` with materials
2. Celery task triggers `IRBAnalyzer`
3. Analyzer gathers materials (uploads + OSF + protocol HTML)
4. Five agents run in parallel using Claude API
5. Findings aggregated and categorized
6. Overall risk level assessed
7. Results saved to database
8. Email notification sent
9. Researcher views report and responds

### Audit Trail

Every review records:
- Who initiated (researcher or committee)
- When initiated and completed
- All uploaded files with SHA256 hashes
- AI model versions used
- Processing time
- All findings and recommendations
- Researcher responses
- Version number (immutable history)

### Integration with IRB Automation Toolkit

The system loads IRB criteria from:
```
IRB_Automation_Toolkit/configs/nicholls_hsirb_settings.json
```

Each agent extracts relevant sections for its focus area. This ensures consistency with Nicholls State University IRB requirements.

---

## Configuration

### Environment Variables

Add to your `.env` file or environment:

```bash
# AI IRB Review
ANTHROPIC_API_KEY=your-api-key-here
IRB_AI_MODEL=claude-3-5-sonnet-20241022
```

### Settings

In `config/settings.py`:

```python
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
IRB_AI_MODEL = config('IRB_AI_MODEL', default='claude-3-5-sonnet-20241022')
IRB_REVIEW_STORAGE = 'media/irb_reviews/'
```

### Dependencies

Required packages (already in `requirements.txt`):
- `anthropic`: Claude API client
- `aiohttp`: Async HTTP for OSF integration
- `PyPDF2`: PDF text extraction
- `python-docx`: Word document extraction

---

## URLs Reference

### Researcher URLs

- **Create Review**: `/studies/<study_id>/irb-review/create/`
- **View Report**: `/studies/<study_id>/irb-review/<version>/`
- **Review History**: `/studies/<study_id>/irb-review/history/`

### Committee URLs

- **Dashboard**: `/studies/committee/`
- **Admin**: `/admin/studies/irbreview/`

---

## Testing

### Test Command

Run a test review for the EI × DK study:

```bash
python manage.py test_irb_review
```

This creates a review and runs it synchronously so you can see results immediately.

### Manual Testing

1. **Create Review**: Go to researcher dashboard → AI IRB Review
2. **Upload Files**: Upload sample protocol, consent form
3. **Wait**: Review runs in background (check email)
4. **View Results**: Click notification link or go to review history
5. **Respond**: Mark issues as addressed, add notes
6. **Re-Review**: Upload updated materials, run new review

---

## Limitations & Disclaimers

### What AI Review CAN Do

✅ Identify common ethical issues
✅ Check for required consent elements
✅ Flag privacy and security concerns
✅ Detect vulnerable population considerations
✅ Provide consistent checklist-based review
✅ Highlight areas for improvement

### What AI Review CANNOT Do

❌ Replace human IRB judgment
❌ Understand nuanced ethical dilemmas
❌ Assess institutional context
❌ Make final approval decisions
❌ Evaluate researcher qualifications
❌ Review statistical methods
❌ Assess community impact

### Important Notes

- **Supplementary Tool**: AI review supplements, not replaces, human review
- **Committee Authority**: Final decisions rest with IRB committee
- **Researcher Responsibility**: You are responsible for all protocol content
- **API Costs**: Running reviews uses Claude API (costs money)
- **Privacy**: Uploaded materials are sent to Anthropic API (encrypted)

---

## Troubleshooting

### Review Status is "Pending" or "Failed"

**Check**:
- Is `ANTHROPIC_API_KEY` configured?
- Is Celery running? (`celery -A config worker`)
- Check Django logs for errors
- Try running test command: `python manage.py test_irb_review`

### No Issues Identified (But You Expected Some)

**Possible Reasons**:
- Materials were minimal or incomplete
- Protocol is actually well-designed!
- AI may have missed subtle issues (human review still needed)
- Try uploading more complete materials

### OSF Integration Not Working

**Check**:
- Is OSF URL correctly formatted? (`https://osf.io/abc123/`)
- Is repository public or do you need authentication?
- Check network connectivity
- View logs for OSF API errors

---

## Best Practices

### For Researchers

1. **Upload Complete Materials**: More context = better analysis
2. **Review Early**: Don't wait until IRB deadline
3. **Iterate**: Run multiple reviews as you improve protocol
4. **Document Responses**: Show committee you addressed issues
5. **Use with Human Review**: Have colleagues review as well

### For Committee Members

1. **Use as Pre-Screen**: Identify obvious issues quickly
2. **Focus Your Review**: AI handles checklist items, you focus on nuance
3. **Track Improvements**: See version history to assess progress
4. **Combine with Traditional Review**: AI + human is most effective

---

## Future Enhancements

Potential additions to the system:

- **Statistical Review Agent**: Check power analysis, sample size
- **Cost-Benefit Agent**: Assess compensation appropriateness
- **Literature Agent**: Verify scientific background and citations
- **Compliance Agent**: Check regulatory compliance (HIPAA, FERPA, etc.)
- **PDF Report Generation**: Download formatted reports
- **Email Digests**: Weekly summaries for committee
- **Integration with IRB Submission System**: Direct submission after review
- **Custom Agent Training**: Train on institution-specific policies

---

## Support

For questions or issues with the AI IRB Review system:

1. **Technical Issues**: Check Django logs and Celery worker logs
2. **Ethical Questions**: Consult with IRB committee
3. **Configuration Help**: Review this guide and check settings
4. **API Issues**: Check Anthropic API status and limits

---

**Remember**: This is a tool to assist and improve your research ethics process, not to replace the essential human judgment and oversight provided by your IRB committee.







