# IRB Protocol Submission Workflow - Implementation Summary

**Implementation Date**: December 2024  
**Status**: ✅ COMPLETE

---

## Overview

A complete IRB protocol submission workflow has been implemented that follows the Nicholls State University HSIRB process. This system handles the full lifecycle from PI submission through college representative review to final decision (approve/revise/reject).

---

## What Was Implemented

### 1. Database Models ✅

**ProtocolSubmission Model** (`apps/studies/models.py`):
- Tracks formal protocol submissions with version control
- Stores PI's suggested review type (exempt/expedited/full)
- Records college rep determination
- Tracks decision status (pending/approved/revise_resubmit/rejected)
- Auto-generates submission numbers (SUB-YYYY-NNN)
- Auto-generates protocol numbers on approval (HSIRB-YYYY-NNN)
- Links to optional AI review
- Supports deception flagging (auto-routes to chair)

**CollegeRepresentative Model**:
- Maps colleges to IRB representatives
- Identifies IRB Chair (Alaina Daigle)
- Supports active/inactive status
- Colleges: Business, Education, Liberal Arts, Sciences, Nursing

**Study Model Enhancement**:
- Added `involves_deception` flag
- Automatically routes deception protocols to chair

### 2. Workflow Logic ✅

**Submission Flow**:
1. PI submits protocol with review type suggestion
2. System assigns college rep based on researcher's department
3. If deception involved → auto-routes to chair (full review)
4. College rep makes initial determination
5. Routing based on review type:
   - **Exempt**: College rep can approve immediately
   - **Expedited**: Requires 2 additional reviewers (assigned by college rep)
   - **Full**: Routes to IRB Chair

**Decision Workflow**:
- **Approve**: Generates protocol number, updates study IRB status
- **Revise & Resubmit**: Records required changes, allows resubmission
- **Reject**: Records rejection grounds

### 3. Views & URLs ✅

**New Views** (`apps/studies/views.py`):
- `protocol_submit`: PI submission form
- `protocol_submission_detail`: View submission details
- `protocol_submission_list`: List all submissions (IRB members)
- `protocol_college_rep_review`: College rep determination
- `protocol_assign_reviewers`: Assign reviewers for expedited reviews
- `protocol_make_decision`: Make decision (approve/R&R/reject)

**URL Patterns** (`apps/studies/urls.py`):
- `/studies/<study_id>/protocol/submit/`
- `/studies/protocol/submissions/`
- `/studies/protocol/submissions/<submission_id>/`
- And related action URLs

### 4. College Representative Assignment ✅

**Automatic Assignment** (`apps/studies/irb_utils.py`):
- Maps researcher's department to college
- Assigns appropriate college representative
- Department → College mapping:
  - Business/Accounting/Finance → Business Administration
  - Education/Psychology → Education & Behavioral Sciences
  - Liberal Arts subjects → Liberal Arts
  - Science/Technology → Sciences & Technology
  - Nursing → Nursing

### 5. Templates ✅

**New Templates**:
- `protocol_submit.html`: Submission form with review type selection
- `protocol_submission_detail.html`: Detailed submission view with decision forms
- `protocol_submission_list.html`: List view for IRB members

**Updated Templates**:
- `researcher_dashboard.html`: Added "Submit Protocol" button

### 6. Admin Interface ✅

**Admin Registration** (`apps/studies/admin.py`):
- `CollegeRepresentativeAdmin`: Manage college reps
- `ProtocolSubmissionAdmin`: Full admin interface for submissions
- List filters, search, and detailed views

### 7. AI Review Integration ✅

**Payment Gating** (`config/settings.py`):
- `AI_REVIEW_ENABLED` setting (default: False)
- Feature visible but disabled until payment configured
- Can be enabled via environment variable

**Integration**:
- Optional AI review during submission
- Links AI review to protocol submission
- Shows AI review results in submission detail

### 8. Management Command ✅

**Setup Command** (`apps/studies/management/commands/setup_college_reps.py`):
- Creates/updates college representatives
- Sets up IRB Chair (Alaina Daigle)
- Creates user accounts if needed
- Usage: `python manage.py setup_college_reps`

---

## Database Migration

**Migration File**: `apps/studies/migrations/0010_protocol_submission_workflow.py`

**To Apply**:
```bash
python manage.py migrate studies
```

---

## Setup Instructions

### 1. Run Migration
```bash
python manage.py migrate studies
```

### 2. Set Up College Representatives
```bash
python manage.py setup_college_reps
```

This will:
- Create user accounts for college reps (if they don't exist)
- Set up college representative assignments
- Mark Alaina Daigle as IRB Chair

### 3. Configure AI Review (Optional)
```bash
# In .env or environment variables
AI_REVIEW_ENABLED=True
ANTHROPIC_API_KEY=your-key-here
```

### 4. Set User Departments
Ensure researcher user profiles have `department` field set so college rep assignment works correctly.

---

## Usage Workflow

### For Primary Investigators

1. **Submit Protocol**:
   - Go to study detail page
   - Click "Submit Protocol"
   - Select review type suggestion
   - Check deception box if applicable
   - Optionally enable AI review
   - Submit

2. **Track Submission**:
   - View submission status on study page
   - Receive notifications at each step
   - Respond to revise & resubmit requests

### For College Representatives

1. **Review Submissions**:
   - Access via Protocol Submissions list
   - Make initial determination
   - Assign reviewers for expedited reviews
   - Approve exempt protocols or route to chair

2. **Make Decisions**:
   - Approve: Issue protocol number
   - Revise & Resubmit: Provide required changes
   - Reject: Provide rejection grounds

### For IRB Chair

1. **Review Full Board Submissions**:
   - All full board reviews route to chair
   - All deception protocols route to chair
   - Make final decisions

---

## Key Features

✅ **Automatic Routing**: Deception protocols automatically route to chair  
✅ **College Rep Assignment**: Based on researcher's department  
✅ **Protocol Number Generation**: Auto-generated on approval (HSIRB-YYYY-NNN)  
✅ **Version Control**: Track multiple submission versions  
✅ **Decision Tracking**: Full audit trail of decisions  
✅ **AI Review Integration**: Optional AI-assisted review  
✅ **Payment Gating**: AI review can be disabled until payment configured  

---

## College Representatives (2024-2025)

- **College of Business Administration**: Dr. Jonathan Murphy
- **College of Education and Behavioral Sciences**: Dr. Grant Gautreaux
- **College of Liberal Arts**: Dr. Linda Martin
- **College of Sciences & Technology**: Dr. Sherry Foret
- **Department of Nursing** (Chair): Dr. Alaina Daigle

---

## Next Steps

1. **Run Migration**: `python manage.py migrate studies`
2. **Set Up Reps**: `python manage.py setup_college_reps`
3. **Test Submission**: Create a test submission as a researcher
4. **Test Review**: Log in as college rep and test review workflow
5. **Configure AI Review**: Enable if payment is configured

---

## Files Modified/Created

**Models**:
- `apps/studies/models.py` (added ProtocolSubmission, CollegeRepresentative, deception flag)

**Views**:
- `apps/studies/views.py` (added protocol submission views)
- `apps/studies/irb_utils.py` (new utility functions)

**Templates**:
- `templates/studies/protocol_submit.html` (new)
- `templates/studies/protocol_submission_detail.html` (new)
- `templates/studies/protocol_submission_list.html` (new)
- `templates/studies/researcher_dashboard.html` (updated)

**Admin**:
- `apps/studies/admin.py` (added admin classes)

**Migrations**:
- `apps/studies/migrations/0010_protocol_submission_workflow.py` (new)

**Management Commands**:
- `apps/studies/management/commands/setup_college_reps.py` (new)

**Settings**:
- `config/settings.py` (added AI_REVIEW_ENABLED)

**URLs**:
- `apps/studies/urls.py` (added protocol submission URLs)

---

## Testing Checklist

- [ ] Run migration successfully
- [ ] Set up college representatives
- [ ] Submit protocol as PI
- [ ] Verify college rep assignment
- [ ] Test exempt review flow
- [ ] Test expedited review flow (assign reviewers)
- [ ] Test full board review flow
- [ ] Test deception routing to chair
- [ ] Test approve decision (protocol number generation)
- [ ] Test revise & resubmit decision
- [ ] Test reject decision
- [ ] Verify AI review integration (if enabled)

---

**Implementation Complete!** 🎉
