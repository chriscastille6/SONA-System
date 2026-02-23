# FERPA Case Law Compliance Audit Report

**System:** SONA System (Participant Recruitment and Management System)  
**Audit Date:** February 6, 2026  
**Auditor:** AI-Assisted Code Audit  
**Scope:** Full codebase review against FERPA case law design rules  

---

## Executive Summary

The SONA System is a Django-based research participant recruitment and IRB protocol management platform deployed at Nicholls State University. The system manages student participants, course enrollments, research credits, prescreening questionnaires, study signups, and AI-assisted IRB reviews.

**Overall Assessment: MODERATE RISK — Remediation Required**

The system has a solid architectural foundation with role-based access controls, UUID primary keys, and a consent-tracking mechanism. However, the audit identified **7 critical findings**, **6 moderate findings**, and **4 minor findings** that require attention to achieve full FERPA compliance under the case law design rules provided.

---

## FERPA Classification of System Data

### Data That IS a FERPA Education Record (Maintained + Identifiable)

Per *United States v. Miami Univ.* (2002), the following system data qualifies as FERPA education records because it is (a) directly related to identifiable students and (b) maintained by the institution:

| Data Element | Model | FERPA Basis |
|---|---|---|
| Course enrollment records | `Enrollment` (participant + course) | Enrollment status maintained by institution |
| Research credit transactions | `CreditTransaction` (participant + study + course + amount) | Academic performance record |
| Study signup records | `Signup` (participant + timeslot + status + attendance) | Attendance and participation records |
| Prescreening responses | `PrescreenResponse` (participant + answers) | Maintained student assessment data |
| No-show counts / ban status | `Profile` (no_show_count, is_banned, ban_reason) | Disciplinary/behavioral records |
| Student ID | `Profile.student_id` | Direct institutional identifier |
| Consent records | `Signup.consent_text_version` | Institutional participation record |

### Data That Is NOT a FERPA Education Record

Per *Owasso v. Falvo* (2002) and *Gonzaga v. Doe* (2002):

| Data Element | Model | Basis for Exclusion |
|---|---|---|
| Anonymous protocol responses | `Response` (session_id, no participant FK) | Anonymous; not linked to identifiable student |
| Study metadata | `Study` (title, description, etc.) | Not student data |
| IRB review analysis | `IRBReview` (AI findings) | Protocol-level, not student-level |
| Protocol submissions | `ProtocolSubmission` | Researcher records, not student records |
| Names alone in user accounts | `User.first_name`, `User.last_name` | Per *Gonzaga*, identifiers alone are not records |

---

## Critical Findings (Severity: HIGH)

### FINDING C-1: AI Prompts Contain Identifiable Study Titles Linked to Researchers — No Prompt Screening

**Rule Violated:** "Implement prompt screening for: student names + academic context, advising content, assessments or evaluations"

**Location:** `apps/studies/irb_ai/agents/base.py` lines 94-134, `apps/studies/irb_ai/analyzer.py` lines 110-149

**Detail:** The `BaseAgent.build_prompt()` method and `IRBAnalyzer.gather_materials()` construct AI prompts that include:
- Study titles (potentially containing researcher/student identifiers)
- Full study descriptions
- Consent form text (may reference specific populations or institutions)
- Uploaded documents (protocol text, recruitment materials, surveys)

These prompts are sent to external AI providers (OpenAI, Anthropic) with **no prompt screening layer** to detect and redact FERPA-protected data that may be embedded in uploaded documents or study descriptions.

**Risk:** If a researcher uploads a document containing student names, grades, advising notes, or assessment data, that content will be sent to an external AI provider without any safeguard.

**Recommendation:**
1. Implement a `FERPAPromptScreener` middleware that scans prompt content before API calls
2. Screen for patterns: student names + academic context, student IDs, grade references, advising content
3. Reject or redact prompts containing FERPA-protected combinations
4. Log screening actions to the audit trail

---

### FINDING C-2: No Audit Logging for AI API Calls

**Rule Violated:** "Do NOT log prompts containing FERPA-protected data outside institutional control" AND "Apply audit logging"

**Location:** `apps/studies/irb_ai/agents/base.py` lines 188-230

**Detail:** The `_call_ai_api()` method sends prompts to OpenAI, Anthropic, or Ollama with **zero audit logging**. There is:
- No record of what was sent to external AI providers
- No record of what was returned
- No tracking of whether FERPA data may have been transmitted
- No differentiation between Ollama (institutional control) vs. OpenAI/Anthropic (outside institutional control)

The only logging is `print()` statements in the analyzer (line 57-77) that go to stdout/log files without structured audit trails.

**Risk:** If FERPA-protected data is sent to an external AI provider, there is no forensic trail to detect, investigate, or report the incident.

**Recommendation:**
1. Log every AI API call to the existing `AuditLog` model with: timestamp, agent name, provider, model, prompt hash (NOT the prompt itself for external calls), response hash
2. For Ollama (institutional), optionally log full prompts
3. For OpenAI/Anthropic (external), log prompt hashes only and flag any calls that contain potential FERPA data
4. Never log full prompts containing FERPA data to external services

---

### FINDING C-3: `submit_response` Endpoint Is CSRF-Exempt and Unauthenticated

**Rule Violated:** "Implement access controls, audit logging, and data minimization"

**Location:** `apps/studies/views.py` lines 380-426

**Detail:** The `submit_response` view is decorated with `@csrf_exempt` and has **no authentication requirement**. It accepts arbitrary JSON payloads, stores IP addresses and user agent strings, and links them to studies. While the `Response` model uses anonymous `session_id` rather than a participant FK (which is good for anonymity), the endpoint:
- Accepts unlimited data in the JSON `payload` field with no validation or sanitization
- Stores IP addresses (which can be identifying metadata)
- Has no rate limiting
- Has no content screening for FERPA-protected data that a client-side form might inadvertently collect

**Risk:** A protocol's client-side code could collect student names, IDs, or other FERPA data and submit it through this endpoint, where it would be stored in the `payload` JSON field without any screening.

**Recommendation:**
1. Add payload schema validation to reject fields that should not be collected
2. Implement rate limiting
3. Add a content screening pass on the payload to flag potential PII/FERPA data
4. Consider whether IP address storage is necessary (data minimization)
5. Document the CSRF exemption rationale (likely needed for cross-origin protocol submissions)

---

### FINDING C-4: Course Credit CSV Export Exposes Full Student Records

**Rule Violated:** "Treat enrollment status, advising notes, assessments, and evaluations as FERPA-protected. Apply access controls, audit logging, and data minimization."

**Location:** `apps/reporting/views.py` lines 25-55

**Detail:** The `course_credits_csv` view exports a CSV file containing:
- Student ID
- Full name
- Email address
- Credits earned
- Credits required
- Completion status

This is a direct export of identifiable education records (enrollment + academic performance). The export:
- Has basic access control (admin or course instructor) but **no audit logging**
- Produces a file that leaves institutional control immediately upon download
- Contains more data than necessary (email may not be needed)

**Risk:** Downloaded CSVs containing FERPA records are outside institutional control. No audit trail records who downloaded what student data and when.

**Recommendation:**
1. Log every CSV export to `AuditLog` with: actor, course, timestamp, record count
2. Apply data minimization — evaluate whether email is necessary in the export
3. Add a FERPA acknowledgment step before download
4. Consider watermarking exports with the downloading user's identity

---

### FINDING C-5: No Data Retention or Deletion Policy Enforcement

**Rule Violated:** "Apply data minimization" and derived data management principles

**Location:** System-wide — no retention policy code found

**Detail:** The system has no automated data retention enforcement. The following data accumulates indefinitely:
- `PrescreenResponse` records (student assessment data)
- `Signup` records (student participation/attendance)
- `CreditTransaction` records (student academic performance)
- `Response` records (protocol response payloads + IP addresses)
- `AuditLog` records (contain metadata about student actions)
- AI review results in `IRBReview` (may contain analysis of student-related content)

**Risk:** Indefinite retention of FERPA records increases breach exposure surface. The longer identifiable education records are maintained, the greater the compliance burden.

**Recommendation:**
1. Implement a data retention policy (configurable per data type)
2. Add management commands to purge expired records
3. Implement IP address anonymization after a defined period (e.g., 90 days)
4. Document retention periods in the system's privacy policy

---

### FINDING C-6: Registration Allows Self-Selection of Privileged Roles

**Rule Violated:** "Apply access controls"

**Location:** `apps/accounts/views.py` lines 17-51

**Detail:** The registration view accepts `role` from the POST request:
```python
role = request.POST.get('role', 'participant')
```
A user can self-assign any role including `admin`, `irb_member`, `researcher`, or `instructor` by manipulating the form submission. There is **no validation** that the requested role is appropriate.

**Risk:** An attacker could register as `admin` or `irb_member` and gain access to all FERPA-protected education records (enrollments, credits, signups, protocol submissions containing student information).

**Recommendation:**
1. Restrict self-registration to `participant` role only
2. Require admin approval for elevated roles (researcher, instructor, irb_member)
3. Add role validation:
```python
SELF_REGISTERABLE_ROLES = ['participant']
if role not in SELF_REGISTERABLE_ROLES:
    role = 'participant'
```

---

### FINDING C-7: AI Agents Have No FERPA-Aware Instructions

**Rule Violated:** "When uncertain, assume FERPA applies and require de-identification or human review"

**Location:** All agent files in `apps/studies/irb_ai/agents/`

**Detail:** While the Privacy agent mentions FERPA in its criteria (`"Does the study comply with privacy regulations (FERPA, etc.)?"` in `privacy.py` line 38), and the Data Security agent mentions FERPA compliance in storage assessment (`data_security.py` line 92), none of the AI agents are instructed to:
- Treat any student-identifiable content in materials as FERPA-protected
- Flag or refuse to process materials containing identifiable student education records
- Default to "FERPA applies" when uncertain
- Require de-identification before analysis

**Risk:** The AI agents will process any content sent to them, including documents containing identifiable student data, without applying FERPA safeguards.

**Recommendation:**
1. Add FERPA-specific instructions to the base agent's system prompt
2. Include the "when uncertain, assume FERPA applies" default
3. Instruct agents to flag any identifiable student data found in materials
4. Add a FERPA compliance finding category to the agent output schema

---

## Moderate Findings (Severity: MEDIUM)

### FINDING M-1: Response Model Stores IP Addresses Without Justification

**Location:** `apps/studies/models.py` line 502

**Detail:** The `Response` model stores `ip_address` as `GenericIPAddressField`. While the `Response` model itself is anonymous (uses `session_id`, no participant FK), IP addresses are indirect identifiers that could enable re-identification, especially on a campus network.

**Recommendation:** Evaluate necessity. If not needed for abuse prevention, remove. If needed, hash or truncate after a short retention period.

---

### FINDING M-2: Profile Model Contains Sensitive Demographic Data

**Location:** `apps/accounts/models.py` lines 106-148

**Detail:** The `Profile` model stores `date_of_birth`, `gender`, `languages`, `student_id`, `ban_reason` — all linked to an identifiable user. The combination of demographics + enrollment + credits constitutes a rich FERPA-protected record.

**Recommendation:** Ensure all views accessing Profile data enforce RBAC. Add audit logging for profile access. Evaluate whether `date_of_birth` needs to be stored (age calculation could use age ranges instead).

---

### FINDING M-3: Study Roster View Exposes Participant PII to Researchers

**Location:** `apps/studies/views.py` lines 317-328

**Detail:** The `study_roster` view shows all signups with participant details to the study researcher. While researchers need to manage participation, the view loads full participant objects (`select_related('participant')`) which includes email, name, etc.

**Recommendation:** Apply data minimization — show only what researchers need (e.g., first name, status). Log roster access. Consider showing participant IDs instead of full names where possible.

---

### FINDING M-4: No Audit Logging for Protocol Submission Access

**Location:** `apps/studies/views.py` lines 981-1022

**Detail:** Protocol submissions contain PI information, co-investigator details, and research descriptions that may reference student populations. Access to protocol submission details is not audit-logged.

**Recommendation:** Log access to protocol submission detail views in `AuditLog`.

---

### FINDING M-5: Consent Text Stored as Snapshot but Not Encrypted

**Location:** `apps/studies/models.py` line 433

**Detail:** `Signup.consent_text_version` stores the full consent text at the time of signup. While this is good practice for informed consent documentation, the consent text combined with the participant FK creates a FERPA-protected record that is stored in plaintext.

**Recommendation:** Consider field-level encryption for consent records, or ensure database-level encryption is configured.

---

### FINDING M-6: AI Review Results Stored Without Access Audit Trail

**Location:** `apps/studies/models.py` lines 519-659, `apps/studies/views.py` lines 576-621

**Detail:** IRB review results (which may contain AI-generated analysis of student-adjacent content) are accessible to multiple roles (researchers, IRB members, admins) but access is not logged to the `AuditLog`.

**Recommendation:** Add audit logging for AI review result access, especially when results contain analysis of student-related protocol content.

---

## Minor Findings (Severity: LOW)

### FINDING L-1: Print Statements Used for Operational Logging

**Location:** `apps/studies/irb_ai/analyzer.py` lines 57-77, `apps/studies/tasks.py` lines 355, 405, 604

**Detail:** Operational logging uses `print()` statements rather than structured logging. Print output may include participant emails (tasks.py line 355: `print(f"Failed to send 24h reminder to {signup.participant.email}: {e}")`).

**Recommendation:** Replace all `print()` statements with `logging.getLogger()`. Ensure participant emails are not logged in error messages.

---

### FINDING L-2: Study Detail View Is Publicly Accessible

**Location:** `apps/studies/views.py` lines 85-98

**Detail:** `study_detail` has no `@login_required` decorator. While study descriptions are not FERPA records, if a study description contains references to specific student populations, this could be a minor concern.

**Recommendation:** No action required for FERPA, but consider whether study details should require authentication.

---

### FINDING L-3: Django Admin Exposes Full Data Model

**Location:** `apps/studies/admin.py` (full file)

**Detail:** The Django admin interface provides full CRUD access to all models including `Signup`, `Response`, `CreditTransaction`, etc. Admin access is controlled by `is_staff`/`is_superuser` but admin actions are not individually audit-logged beyond Django's built-in `LogEntry`.

**Recommendation:** Configure Django admin audit logging. Consider restricting admin access to FERPA-protected models.

---

### FINDING L-4: Email Notifications Include Internal URLs

**Location:** `apps/studies/tasks.py` (throughout)

**Detail:** Email notifications include direct URLs to submission details, review reports, and study dashboards. While URLs alone don't expose FERPA data, they could allow unauthorized access if forwarded.

**Recommendation:** Ensure all linked pages enforce authentication. Consider using time-limited tokens in notification URLs.

---

## Compliance Matrix

| FERPA Design Rule | Status | Findings |
|---|---|---|
| Anonymous/ungraded student work may be processed by AI | **PARTIAL** | Response model is anonymous (good), but no screening prevents graded/identified data from entering AI | C-1, C-7 |
| AI may accept student name alone; don't combine with academic context without controls | **FAIL** | No prompt screening for name + academic context combinations | C-1 |
| Treat enrollment, attendance, performance, advising as FERPA-protected | **PARTIAL** | Data exists and has basic RBAC, but lacks audit logging and data minimization | C-4, M-3, M-4 |
| AI may process anonymized data; don't retain re-identification keys | **PARTIAL** | Response model is anonymous, but IP address storage creates re-identification risk | M-1 |
| AI outputs tied to students must be treated as FERPA records | **PARTIAL** | AI reviews are study-level not student-level (good), but no safeguard prevents student-level outputs | C-7 |
| Do NOT train/fine-tune on identifiable student education records | **PASS** | No training or fine-tuning code found; system uses inference-only API calls |
| Do NOT log prompts with FERPA data outside institutional control | **FAIL** | No logging distinction between institutional (Ollama) and external (OpenAI/Anthropic) providers | C-2 |
| Implement prompt screening | **FAIL** | No prompt screening exists | C-1 |
| When uncertain, assume FERPA applies | **FAIL** | No default-to-FERPA logic in AI agents or data handling | C-7 |
| FERPA enforcement depends on documented controls, governance, and technical safeguards | **PARTIAL** | Some controls exist (RBAC, audit signals), but gaps in logging, screening, and retention | Multiple |

---

## Recommended Priority Actions

### Immediate (Week 1-2)
1. **Fix role self-selection vulnerability** (C-6) — Trivial code change, critical security impact
2. **Implement prompt screening middleware** (C-1) — Prevent FERPA data from reaching external AI providers
3. **Add AI API call audit logging** (C-2) — Track what data leaves institutional control

### Short-Term (Week 3-4)
4. **Add audit logging for data exports** (C-4) — Log CSV downloads of student records
5. **Add FERPA instructions to AI agent prompts** (C-7) — Update base agent system prompt
6. **Validate response payloads** (C-3) — Schema validation and PII screening

### Medium-Term (Month 2)
7. **Implement data retention policies** (C-5) — Automated purge/anonymization of aged records
8. **Add audit logging for sensitive view access** (M-4, M-6) — Protocol submissions, AI reviews
9. **Review data minimization in roster and export views** (M-3, C-4)
10. **Replace print statements with structured logging** (L-1)

### Long-Term (Quarter 2)
11. **Implement field-level encryption** for consent records and demographic data (M-2, M-5)
12. **IP address anonymization pipeline** (M-1)
13. **Comprehensive FERPA compliance documentation** for Department of Education readiness

---

## What the System Does Well

1. **Anonymous protocol responses** — The `Response` model uses `session_id` instead of participant FK, implementing genuine anonymization per *Owasso v. Falvo*.
2. **Role-based access control** — Clear role hierarchy (admin, irb_member, researcher, instructor, participant) with view-level enforcement.
3. **UUID primary keys** — All models use UUIDs, preventing enumeration attacks on student records.
4. **Consent versioning** — `Signup.consent_text_version` snapshots consent at participation time.
5. **IRB audit trail** — `AuditLog` model and signal-based tracking of IRB status changes.
6. **AI review gating** — `AI_REVIEW_ENABLED` feature flag controls AI review activation.
7. **Ollama support** — Option to keep AI processing entirely within institutional control.
8. **Document integrity** — `ReviewDocument.file_hash` provides SHA256 integrity verification.
9. **Production security** — SSL redirect, HSTS, secure cookies, CSRF protection in production mode.
10. **Argon2 password hashing** — Best-practice password storage.

---

*This audit was conducted through static code analysis of the full SONA System codebase. Dynamic testing (runtime behavior, database content, network traffic analysis) was not performed and is recommended as a follow-up.*
