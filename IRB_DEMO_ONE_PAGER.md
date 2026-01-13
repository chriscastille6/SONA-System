# SONA System Demo - One-Page Summary for IRB Review

## 🎯 Quick Access

| Access Point | URL | Credentials |
|--------------|-----|-------------|
| **Main System** | https://nichollsirb.up.railway.app | See below |
| **Admin Panel** | https://nichollsirb.up.railway.app/admin/ | admin@university.edu / demo123 |

## 🔑 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| **Researcher** | researcher@nicholls.edu | demo123 |
| **Participant** | emily.johnson@my.nicholls.edu | demo123 |
| **Admin/IRB** | admin@university.edu | demo123 |

## 💰 ROI Summary

| Item | Value |
|------|-------|
| **5-Year Cost Savings** | $13,500-25,000 vs. commercial SONA |
| **Annual Time Savings** | 425 hours (~$12,750 value) |
| **Total 5-Year ROI** | **$88,750+** |
| **Per-User Fees** | $0 (unlimited users) |

### Cost Comparison

- **Commercial SONA Systems:** $15,000-25,000 (5 years)
- **This System (hosted):** $1,500-3,600 (5 years)
- **This System (university VM):** $0 (5 years)

## ✅ IRB-Critical Features

### Compliance & Oversight
- ✓ Real-time IRB status tracking (approved, pending, exempt, expired)
- ✓ Automated expiration alerts
- ✓ IRB protocol numbers and dates
- ✓ OSF (Open Science Framework) integration

### Consent Management
- ✓ Versioned consent forms (audit trail)
- ✓ Timestamp when each participant consented
- ✓ Easy verification of consent version
- ✓ Re-consent workflow if changes required

### Data Protection
- ✓ Role-based access control
- ✓ Anonymous protocol responses (no PII)
- ✓ Complete audit logs
- ✓ Secure password hashing (Argon2)
- ✓ CSRF/XSS/SQL injection protection

### Ethical Research
- ✓ Bayesian sequential monitoring (early stopping)
- ✓ Minimizes participant burden
- ✓ Prevents unnecessary data collection
- ✓ Configurable sample size limits

### Reporting & Audit
- ✓ CSV exports for IRB reviews
- ✓ Participation statistics
- ✓ Credit transaction audits
- ✓ Immutable record keeping

## 🚀 15-Minute Demo Guide

### As Researcher (5 min)
1. Login → Researcher Dashboard
2. View "Decision Making Under Uncertainty" study
3. Check IRB status (IRB-2025-089, approved)
4. Review attendance records (23 signups, 80% attendance)
5. View protocol responses (12 complete datasets)

**IRB Focus:** IRB tracking, consent versioning, audit trail

### As Participant (5 min)
1. Login → Available Studies
2. Review study description and consent form
3. Book a timeslot
4. View "My Bookings" and "My Credits"

**IRB Focus:** Clear consent, voluntary participation, easy withdrawal

### As Admin/IRB (5 min)
1. Admin panel → Studies
2. Review IRB fields, OSF settings, monitoring config
3. Check Signups (consent timestamps)
4. Review Credit Transactions (audit trail)
5. View Users (role-based access)

**IRB Focus:** Complete oversight, audit capability, compliance verification

## 📊 Demo Data Included

- **1 Active Study** with IRB approval
- **15 Users** (researcher, instructor, 12 participants, admin)
- **45 Timeslots** (past and future)
- **23 Signups** with complete attendance history
- **12 Protocol Responses** with rich data
- **15 Credit Transactions** with audit trail

## 🛠️ IRB Automation Toolkit

**Bonus Feature:** Automated IRB application preparation
- Screenshot capture automation
- Document generation (PDF + Word) with Nicholls HSIRB formatting
- Consent form templates
- Verification scripts

**Time Saved:** ~2 hours per IRB application

## 🔍 Key Questions for Your Review

1. Is the consent workflow IRB-compliant?
2. Are privacy protections adequate?
3. Can IRB staff easily verify compliance?
4. Is participant withdrawal sufficiently accessible?
5. Does record-keeping meet documentation requirements?
6. Are there any ethical concerns?
7. What additional features would help IRB oversight?

## 📈 Why This Matters

**For IRB:** Enhanced compliance tracking, better documentation, automated alerts

**For Researchers:** Reduced administrative burden, streamlined processes, time savings

**For Institution:** Massive cost savings, data sovereignty, no vendor lock-in

**For Participants:** Clear consent, easy access, transparent credit tracking

## 📞 Contact & Next Steps

1. **Try the demo** (~15 minutes with credentials above)
2. **Review IRB features** from admin perspective
3. **Share feedback** on compliance and ethics
4. **Schedule walkthrough** if interested (optional)

---

## 🔗 Live Demo Links

**Main System:** https://nichollsirb.up.railway.app  
**Admin Panel:** https://nichollsirb.up.railway.app/admin/

All demo accounts use password: **demo123**

---

## 🧪 Conjoint Analysis Study (IRB Approved)

- **Title (SONA):** `Conjoint Analysis Study` (`slug: conjoint-analysis`)
- **Researchers:** Dr. Christopher Castille (PI inside SONA) with Dr. Martin Meder as classroom lead
- **IRB Status:** Approved – packet copied into `media/irb/conjoint-analysis/`
- **IRB Reviewer:** Jon Murphy (IRB member dashboard includes approval files + toggle for email alerts)
- **In-app materials:**
  - Study updates attach the PDF/DOCX IRB application and the `SONA_IRB_Summary.md`
  - IRB Committee dashboard cards now include a `View Study Status` button that surfaces the approval documents
- **Eligibility:** Labor Economics students, age 18+

To review the packet inside the app:
1. Log in as the researcher (`christopher.castille@nicholls.edu`) or IRB reviewer (`jonathan.murphy@nicholls.edu`).
2. Open `/studies/irb/dashboard/` or `/studies/committee/`, select **View Study Status**, and download the files listed under **IRB Updates & Notifications**.

To trigger a notification smoke test for the IRB reviewers:

```bash
python manage.py send_irb_test_email conjoint-analysis
```

---

## 🧭 IRB Member Onboarding (Prototype)

- **Create an IRB reviewer account + assignment**
  ```bash
  python manage.py create_irb_member jonathan.murphy@nicholls.edu \
    --first-name Jonathan \
    --last-name Murphy \
    --study conjoint-analysis-pilot
  ```
  - Auto-generates a password (or pass `--password`), verifies email, sets IRB role, and subscribes the reviewer to notifications for the specified study.
- **Disable emails (optional):** append `--disable-email-updates`
- **Grant Django admin access (optional):** append `--staff`
- **Toggle email alerts (IRB dashboard):** IRB reviewers can pause/resume notifications from the dashboard’s “Pause/Enable email alerts” button.
- **SMTP smoke test:** `python manage.py send_irb_test_email <study-slug>` to verify that assigned IRB reviewers receive messages once SMTP settings are in place.
- **IRB reviewer dashboard:** `/studies/irb/dashboard/` (live notifications, latest AI review, researcher updates, attachments)
- **Researcher live updates:** Researchers post updates from the study status page (`/studies/<slug>/status/`) and assigned IRB members receive email/IRB dashboard alerts in real time.

---

## Technical Specs

**Platform:** Django 5.0 (Python)  
**Database:** PostgreSQL (Railway hosting)  
**Security:** Industry best practices  
**Hosting:** Railway.app (cloud deployment)  
**Status:** Production-ready, security audited

**Open Source:** MIT License, full code transparency

---

**Created for Nicholls State University Research Community**  
**With AI Assistance - October 2025**

