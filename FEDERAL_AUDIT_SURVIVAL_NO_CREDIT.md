# Federal Audit Survival: SONA Without Course Credit or Bonus Points

**Context:** SONA/PRAMS is live but shadow IT. You could formalize (localize) or purchase a SONA system (~$2K). You want to keep developing it but **will not use course credit or monitor bonus points**. What is required to survive a federal audit?

---

## Why No Credit/Bonus Changes Everything

**With course credit or bonus points**, the system creates FERPA education records:
- `CreditTransaction` links participant → study → course → amount (academic performance)
- `Enrollment` links participant → course (enrollment status)
- `Signup` + attendance links participation to grades

**Without credit or bonus points**, participation is **voluntary research**—not used for grading. Per Cornell IRB guidance and case law (*Owasso v. Falvo*, *Hardin County Schools v. Foster*), voluntary research data not used for institutional decisions is **not** FERPA-protected education records in the same way as graded, required records.

---

## Minimum Requirements to Survive a Federal Audit

### 1. **45 CFR 46 (Common Rule) — Human Subjects Protection** ✅ Still applies

| Requirement | What You Need |
|-------------|---------------|
| IRB oversight | All studies have IRB approval; protocols in PRAMS |
| Informed consent | Documented, voluntary; consent text versioned |
| Risk minimization | Minimal-risk studies; debriefing where appropriate |
| Data security | Encryption in transit (TLS), access controls |

### 2. **FERPA — Greatly Reduced Scope** ✅ Without credit/bonus

| Data | With Credit | Without Credit |
|------|-------------|-----------------|
| CreditTransaction | FERPA record | **Not used** — remove or disable |
| Enrollment (for credit allocation) | FERPA record | **Not needed** — optional |
| Signup + attendance | FERPA (grade linkage) | **Voluntary** — not education record |
| Anonymous Response (session_id only) | Not FERPA | Not FERPA |
| Protocol submissions | Not FERPA | Not FERPA |

**Key:** Keep research data **anonymous or de-identified**. No link between participation and institutional student records (grades, enrollment for credit).

### 3. **Data Security (Baseline)**

| Control | Purpose |
|---------|---------|
| TLS/HTTPS | Encryption in transit |
| Role-based access | Researchers see only their studies; IRB sees protocols |
| Audit logging | Who accessed what, when (sensitive views, exports) |
| No PII in research payloads | Response model uses session_id, not participant FK |

### 4. **Audit Trail (Minimum)**

- Protocol submissions: who submitted, when, decision
- IRB approvals: who approved, when
- Data exports: log CSV downloads of any participant-linked data (if any)
- AI API calls: log that calls occurred (hash, not content) when using external providers

### 5. **Data Retention**

- Document retention policy (e.g., 5 years post-study per IRB)
- Purge or anonymize when no longer needed

---

## What You Can Safely Disable or Simplify

| Feature | With Credit | Without Credit |
|---------|-------------|-----------------|
| CreditTransaction | Required | **Disable** — no credit to allocate |
| Enrollment (for credit) | Required | **Optional** — only if needed for other reasons |
| Bonus-point tracking | Required | **Disable** |
| Prescreening (if links to student) | FERPA risk | **Use anonymous prescreen** or disable |
| Student ID in Profile | FERPA identifier | **Don't collect** for research participants |

---

## Formalization Options

| Option | Cost | Audit Posture |
|--------|------|---------------|
| **Keep as shadow IT** | $0 | Higher risk: no formal IT approval, no vendor assessment |
| **Localize/formalize** | Dev time | Better: institutional hosting, documented controls, audit trail |
| **Purchase SONA (~$2K)** | $2K | Best: vendor-assessed, supported, known compliance profile |

---

## Recommended Minimum (No Credit/Bonus)

1. **Disable** credit allocation and bonus-point features
2. **Use** anonymous participation (session_id, no participant FK for research data)
3. **Document** that participation is voluntary and not used for grades
4. **Maintain** IRB approval for all studies
5. **Add** audit logging for protocol submissions, IRB decisions, and any data exports
6. **Restrict** self-registration to participant role only (fix C-6 from FERPA audit)
7. **Retain** consent records and protocol documentation per IRB requirements

---

## References

- FERPA: 34 C.F.R. § 99; *Owasso v. Falvo* (2002); *Hardin County Schools v. Foster* (2018)
- Common Rule: 45 CFR 46
- FERPA Audit: `FERPA_AUDIT_REPORT.md`
- Cornell IRB: Voluntary research not for grades = not FERPA education records
