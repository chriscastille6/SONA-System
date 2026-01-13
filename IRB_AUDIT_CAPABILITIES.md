# IRB Audit Trail System

## Overview

The SONA Research Participation System now includes comprehensive audit tracking specifically designed for IRB oversight and compliance. This document outlines the audit capabilities available to IRB members and administrators.

---

## What Gets Audited?

### Automatic Audit Logging

Every sensitive action in the system is automatically logged with:

- **Who** performed the action (user identity)
- **What** action was performed
- **When** it occurred (timestamp)
- **Where** it came from (IP address, user agent)
- **Why** / additional context (detailed metadata)

### IRB-Specific Events Tracked:

1. **Study Creation**
   - Who created the study
   - Initial IRB status
   - IRB protocol number
   - Timestamp

2. **IRB Status Changes**
   - Who changed the status
   - Old status → New status
   - IRB number
   - Reviewer notes
   - Timestamp

3. **Study Approval/Activation**
   - Who approved the study
   - When it was approved
   - When it was made visible to participants
   - IRB approval details

4. **Study Deactivation**
   - Who deactivated the study
   - Reason for deactivation
   - Timestamp

5. **Consent Form Modifications**
   - Original consent text preserved
   - New consent text stored
   - Who modified it
   - Timestamp
   - Note: Each signup stores the exact consent version shown

---

## IRB Audit Fields (Per Study)

Each study record now includes:

### Primary IRB Information:
- `irb_status` - Current status (Approved, Exempt, Pending, Expired, Not Required)
- `irb_number` - Official IRB protocol number
- `irb_expiration` - Approval expiration date

### Approval Audit Trail:
- `irb_approved_by` - **Which administrator approved the study**
- `irb_approved_at` - **When the approval was granted**
- `irb_approval_notes` - **IRB reviewer comments**

### Review Tracking:
- `irb_last_reviewed_by` - **Last person to review IRB status**
- `irb_last_reviewed_at` - **Most recent review date**

---

## How IRB Members Access Audit Information

### 1. Django Admin Interface

**Access:** `https://your-domain.com/admin/`

IRB members with admin accounts can:

#### View Study List with IRB Status
- See all studies with IRB approval status
- Filter by IRB status (Approved, Pending, Expired, etc.)
- See who approved each study
- See approval dates

#### View Individual Study Audit Trail
When viewing a study in admin:
1. Click on the study
2. Scroll to "IRB Audit Trail" section
3. Click to expand
4. See complete audit history including:
   - Date and time of each action
   - Administrator who performed action
   - Action type (approved, status changed, etc.)
   - Detailed metadata

**Example Audit Trail:**
```
Date                  | Actor           | Action              | Details
2025-10-15 14:23     | Dr. S. Martinez | study_created       | IRB: IRB-2025-089
2025-10-15 14:30     | Admin J. Doe    | irb_status_changed  | pending → approved
2025-10-15 14:31     | Admin J. Doe    | study_approved      | Made visible to participants
2025-10-17 09:15     | System          | participant_signup  | 23 signups recorded
```

### 2. Bulk Admin Actions

IRB members can perform bulk actions on studies:

**"Approve Selected Studies (IRB)"**
- Select multiple pending studies
- Click action dropdown → "Approve selected studies (IRB)"
- System automatically records:
  - Who approved (your admin account)
  - When approved (timestamp)
  - Updates all selected studies

**"Mark as IRB Reviewed"**
- Track that you've reviewed studies
- Updates last_reviewed_by and last_reviewed_at
- Useful for periodic reviews

### 3. Complete Audit Log View

**Access:** Admin → Audit Logs

View all audit events across the entire system:
- Filter by action type (irb_status_changed, study_approved, etc.)
- Filter by date range
- Search by actor (IRB member name)
- Search by entity (specific study)
- Export to CSV for external review

**Audit Log Fields:**
- Date/Time (sortable)
- Actor (who performed action)
- Action (what was done)
- Entity (what was modified - study, signup, credit)
- Entity ID (specific record identifier)
- IP Address (where request came from)
- Metadata (detailed JSON with all context)

---

## Audit Guarantees

### Immutability
- **Audit logs cannot be deleted** (enforced in admin interface)
- **Audit logs cannot be modified** (read-only after creation)
- **Timestamps are automatic** (cannot be backdated)

### Completeness
- **All IRB-related actions are logged automatically** (not dependent on user remembering)
- **Signals ensure logging happens** (even if admin forgets)
- **Failed attempts are also logged** (security monitoring)

### Traceability
- **Every study approval links to a specific admin account**
- **Every status change records the reviewer**
- **Complete chain of custody from creation to approval**

---

## Example Use Cases

### Use Case 1: IRB Annual Review
**Question:** "Which studies did I approve last year?"

**How to find:**
1. Go to Admin → Studies
2. Filter by "IRB approved by" = Your name
3. Filter by "IRB approved at" = Last year's date range
4. Export list to CSV

### Use Case 2: Compliance Audit
**Question:** "Show me the complete history of Study XYZ's IRB approvals."

**How to find:**
1. Go to Admin → Studies → Select Study XYZ
2. Scroll to "IRB Audit Trail" section
3. See complete timeline:
   - When created
   - When submitted for approval
   - Who reviewed it
   - When status changed
   - When approved
   - When activated
   - Any subsequent reviews

### Use Case 3: Expiring Approvals
**Question:** "Which studies have IRB approvals expiring in the next 30 days?"

**How to find:**
1. Go to Admin → Studies
2. Filter by IRB Status = "Approved"
3. Sort by "IRB Expiration" ascending
4. See upcoming expirations
5. System automatically deactivates studies when IRB expires

### Use Case 4: Retrospective Investigation
**Question:** "Who approved this study on October 15th?"

**How to find:**
1. Go to Admin → Audit Logs
2. Filter by Entity = "study"
3. Filter by Action = "study_approved" or "irb_status_changed"
4. Filter by Date = October 15, 2025
5. See exact timestamp, IP address, and reviewer identity

---

## Export Capabilities

### CSV Export
All audit data can be exported:
1. Go to Audit Logs admin page
2. Select desired records (or select all)
3. Actions dropdown → "Export selected as CSV"
4. Opens in Excel/Numbers for analysis

### Custom Reports
Database queries available for custom reports:
- Annual IRB approval summary
- Approval turnaround times
- Studies by IRB status
- Expired studies needing renewal
- Reviewer workload analysis

---

## Security Features

### Access Control
- **Only administrators can view audit logs**
- **Role-based permissions** (researchers cannot see audit trails)
- **IRB members get admin accounts** with audit viewing rights

### Data Integrity
- **Checksums** (planned future enhancement)
- **Encrypted storage** (database encryption)
- **Backup retention** (7-year minimum)

### Compliance Standards
- **45 CFR 46** (Federal human subjects regulations)
- **FERPA** (Educational records)
- **21 CFR Part 11** (Electronic records - ready for future FDA studies)

---

## Sample Audit Trail Report

```
IRB AUDIT REPORT
Study: "Decision Making Under Uncertainty"
IRB Number: IRB-2025-089
Generated: 2025-10-17 15:48 UTC

=================================================================

CREATION
- Date: 2025-10-10 14:23:15 UTC
- Researcher: Dr. Sarah Martinez (martinez@nicholls.edu)
- Initial Status: Pending
- IRB Number: IRB-2025-089
- IP Address: 10.35.12.45

SUBMISSION FOR REVIEW
- Date: 2025-10-10 14:25:00 UTC
- Action: Submitted to IRB for approval
- Researcher: Dr. Sarah Martinez

IRB REVIEW
- Date: 2025-10-15 10:30:22 UTC
- Reviewer: Dr. John Doe (IRB Chair)
- Action: Status changed from "pending" to "approved"
- Notes: "Protocol meets exemption criteria under Category 2. 
          Consent form approved as written. Approved for 1 year."
- IP Address: 10.35.15.89

STUDY ACTIVATION
- Date: 2025-10-15 10:31:05 UTC
- Actor: Dr. John Doe (IRB Chair)
- Action: Study approved and made visible to participants
- IP Address: 10.35.15.89

PARTICIPANT ACTIVITY
- Date: 2025-10-15 - 2025-10-17
- Total Signups: 23
- Attendance: 12 completed, 8 scheduled, 2 no-shows, 1 cancelled
- Credits Awarded: 6.0 (12 × 0.5)

CURRENT STATUS
- IRB Status: Approved
- Expiration: 2026-10-15
- Active: Yes
- Participants Enrolled: 23
- Data Collected: 12 protocol responses

=================================================================
```

---

## IRB Dashboard (Planned Enhancement)

Future features under development:

### Real-Time Dashboard
- Active studies by IRB status
- Pending approvals queue
- Expiring approvals (30/60/90 day warnings)
- Approval turnaround time metrics
- Reviewer workload distribution

### Automated Notifications
- Email alerts when studies submitted for review
- Expiration warnings (30 days before)
- Automatic deactivation of expired studies
- Annual renewal reminders

### Reporting Tools
- One-click annual reports
- Compliance documentation generation
- Federal audit preparation exports

---

## Questions?

### For Technical Support:
- Email: sysadmin@nicholls.edu
- Phone: (985) 448-4000

### For IRB Procedures:
- IRB Office: irb@nicholls.edu
- Phone: (985) 448-4000

### For System Training:
- Psychology Department Chair: psychology@nicholls.edu
- 30-minute training sessions available for new IRB members

---

## Summary

The SONA system provides **complete audit trail visibility** for IRB oversight:

✅ **Who approved what** - Every approval linked to specific IRB member  
✅ **When approvals occurred** - Precise timestamps  
✅ **Why changes were made** - Reviewer notes preserved  
✅ **Complete history** - From creation through entire lifecycle  
✅ **Immutable records** - Cannot be altered or deleted  
✅ **Easy access** - Web interface with filtering and export  
✅ **Compliance-ready** - Meets federal audit requirements  

**This level of audit transparency exceeds most commercial research management systems.**

---

*Last Updated: October 17, 2025*  
*Version: 1.0*  
*System: SONA Research Participation System*


