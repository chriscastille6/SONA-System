# Security & Compliance Remediation List

**Classification:** Internal — Lead Architect  
**Scope:** Pre–IT review remediation (NIST/FERPA, OWASP, IRB 45 CFR 46)  
**Date:** February 2026  

---

## HIGH SEVERITY

### H-1. Privilege Escalation via Registration (Authentication/RBAC)

**Risk:** A malicious user can self-assign `admin`, `irb_member`, or `researcher` by submitting `role` in the registration form. This violates NIST/FERPA role separation and allows full system compromise.

**Location:** `apps/accounts/views.py` — `register()`  

**Current code (vulnerable):**
```python
role = request.POST.get('role', 'participant')
# ...
user = User.objects.create_user(
    email=email,
    password=password,
    first_name=first_name,
    last_name=last_name,
    role=role  # ← User-controlled
)
```

**Fix:** Ignore client-supplied role; force participant for self-registration. Restrict other roles to admin or invite-only flows.

```python
# In register(), replace:
role = request.POST.get('role', 'participant')
# with:
role = 'participant'  # Self-registration is participant only; other roles via admin/invite only.
```

If you need to support closed/invite-only registration for researchers, use a separate admin-created invite token or post-registration role assignment by an admin — never trust `request.POST.get('role')` for privilege roles.

---

### H-2. CSRF Exemption on Protocol Response API (OWASP CSRF)

**Risk:** `submit_response` is decorated with `@csrf_exempt`. Cross-site requests can submit protocol responses on behalf of users or inject data into any study, enabling data poisoning and compliance violations.

**Location:** `apps/studies/views.py` — `submit_response`  

**Current code (vulnerable):**
```python
@csrf_exempt
@require_http_methods(["POST"])
def submit_response(request, study_id):
```

**Fix (choose one):**

- **Option A — Same-origin only (recommended if used by your own front-end):** Remove `@csrf_exempt` and ensure the front-end sends the CSRF token (e.g. in header or body) for same-origin requests. Keep `CsrfViewMiddleware` enabled.

- **Option B — External/embedded protocol (e.g. iframe from another domain):** Do not disable CSRF globally. Use a per-study or per-session token (e.g. in URL or one-time link) that is validated in the view instead of the Django CSRF cookie. Example pattern:

```python
# Remove @csrf_exempt. In submit_response, after loading the study:
submission_token = request.POST.get('submission_token') or request.headers.get('X-Submission-Token')
if not submission_token or not validate_protocol_submission_token(study_id, submission_token):
    return JsonResponse({'error': 'Invalid or missing submission token'}, status=403)
```

Implement `validate_protocol_submission_token()` using a signed or HMAC token (with a server-side secret from settings) so only your protocol pages can generate valid tokens.

---

### H-3. IDOR on Mark-Attendance View (OWASP IDOR)

**Risk:** Any authenticated user can request `GET /studies/researcher/signup/<uuid>/attendance/` for any signup UUID. The view loads the signup then checks permission and redirects — but the response is still rendered first (or the redirect happens after the object is loaded), exposing another participant’s PII (name, email) in the mark-attendance page. This is an Insecure Direct Object Reference and FERPA disclosure.

**Location:** `apps/studies/views.py` — `mark_attendance()`  

**Current code (vulnerable):**
```python
signup = get_object_or_404(Signup, pk=pk)
# Check permission
if signup.timeslot.study.researcher != request.user and not request.user.is_admin:
    messages.error(request, 'Access denied.')
    return redirect('studies:researcher_dashboard')
# ... later renders template with signup (participant name, email)
```

**Fix:** Enforce authorization before rendering. Return 404 for unauthorized users so existence of the signup is not disclosed and no PII is shown.

```python
@login_required
def mark_attendance(request, pk):
    """Mark attendance for signup."""
    signup = get_object_or_404(Signup, pk=pk)
    study = signup.timeslot.study
    if study.researcher != request.user and not getattr(request.user, 'is_admin', False):
        from django.http import Http404
        raise Http404()
    # ... rest unchanged (POST handling, render)
```

Ensure the template is only rendered for users who passed this check (current flow already does this after the fix, since you 404 instead of redirect).

---

### H-4. Unauthenticated Protocol Response Submission (Authentication / Data Integrity)

**Risk:** `submit_response` does not require authentication. Anyone who can reach the endpoint can POST to any `study_id`, creating `Response` records for any study. This allows data poisoning and undermines IRB/data integrity.

**Location:** `apps/studies/views.py` — `submit_response`; `config/api_urls.py`  

**Fix:**

1. **Restrict to approved/active studies only** so unapproved or inactive studies cannot receive submissions:
   ```python
   study = get_object_or_404(Study, pk=study_id)
   if not study.is_active or not study.is_approved:
       return JsonResponse({'error': 'Study not available for submissions'}, status=403)
   ```

2. **Optional but recommended:** Require a shared secret or signed link for anonymous studies (e.g. token in URL or header) so only your protocol pages can submit, and log `ip_address`/`user_agent` (you already store these on `Response`) for audit.

3. **Rate limiting:** Add rate limiting (e.g. by IP or by study_id) to prevent abuse (e.g. `django-ratelimit` or reverse-proxy limits).

---

## MEDIUM SEVERITY

### M-1. SECRET_KEY Fallback in Production (Environment / Secrets)

**Risk:** If `SECRET_KEY` is not set in the environment, Django uses a hardcoded default. Session/signing compromise and key reuse across deployments.

**Location:** `config/settings.py`  

**Current code:**
```python
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
```

**Fix:** Fail fast in production when `SECRET_KEY` is missing.

```python
_SECRET_KEY = config('SECRET_KEY', default=None)
if not DEBUG and not _SECRET_KEY:
    raise RuntimeError('SECRET_KEY must be set in environment (e.g. .env) for production.')
SECRET_KEY = _SECRET_KEY or 'django-insecure-change-me-in-production'
```

Place this after `DEBUG = config(...)` so `DEBUG` is defined. Alternatively, remove the default entirely and ensure production always sets `SECRET_KEY` in the environment.

---

### M-2. Audit Trail Gaps (IRB / 45 CFR 46)

**Risk:** IRB and FERPA require immutable(ish) logs for “who approved a study,” “who granted credit,” and “when did a student consent.” Today:
- **Study approval / IRB status:** Covered by `Study` save signals → `AuditLog` (study_created, irb_status_changed, study_approved).
- **Consent:** Only on `Signup.consented_at` / `consent_text_version` — not written to `AuditLog`.
- **Credit grant:** `CreditTransaction` has no signal → no `AuditLog` entry when credits are granted.

**Locations:** `apps/studies/signals.py`; `apps/credits/models.py` (no signal); credit grant flow.

**Fix:**

1. **Consent:** When a signup is created (participant books and consents), add an audit log entry:
   - In `apps/studies/signals.py` (new receiver for `Signup`):
     - On `post_save` and `created=True`, create `AuditLog(action='participant_consent', entity='signup', entity_id=instance.id, metadata={'study_id': str(instance.timeslot.study_id), 'consented_at': instance.consented_at.isoformat()}, actor=instance.participant)`.
   - Or call a small helper from the view that creates the signup and then creates the `AuditLog` (so consent is explicitly logged at book time).

2. **Credit grant:** When a `CreditTransaction` is created, log it:
   - Add a `post_save` receiver on `CreditTransaction` in `apps/credits/` (e.g. in `signals.py` or in the app’s `apps.py` ready()):
     - `AuditLog.objects.create(action='credit_granted', entity='credit', entity_id=instance.id, actor=request.user or instance.created_by, metadata={'participant_id': str(instance.participant_id), 'amount': str(instance.amount), 'study_id': str(instance.study_id) if instance.study_id else None})`.
   - Ensure `created_by` is set in the view when implementing the grant form.

3. **Immutability:** Prefer append-only retention for `audit_logs` (e.g. no deletes/updates in application code; DB permissions if possible). Optionally capture `ip_address` and `user_agent` in `AuditLog` where the request is available (e.g. in views when creating logs).

---

### M-3. Message Template Uses `|safe` (XSS)

**Risk:** `templates/base.html` uses `{{ message|safe }}` for Django messages. If any view ever adds user-controlled or unsanitized content to messages, it becomes stored XSS. Currently many messages use `format_html` with escaped interpolations, but the pattern is risky.

**Location:** `templates/base.html`  

**Fix:** Avoid rendering raw HTML from messages unless you strictly control every message. Prefer one of:

- **Option A:** Use plain text only for messages and remove `|safe` so all message content is auto-escaped:
  ```django
  {{ message }}
  ```
  Then replace any `format_html` success messages with plain strings (e.g. include URLs as plain text, not clickable HTML).

- **Option B:** If you must allow limited HTML (e.g. links), use a sanitizer (e.g. `bleach`) in a custom template filter and apply it to `message` instead of `|safe`, so only allow tags you need (e.g. `<a>`, `<strong>`).

---

### M-4. Co-Investigator Check Case-Sensitivity (Consistency / Minor IDOR)

**Risk:** In `amendment_create`, co-investigator check uses `request.user.email in submission.co_investigators`, while elsewhere (e.g. `protocol_submission_detail`) the check uses `.lower()`. Inconsistent casing could allow or deny access incorrectly.

**Location:** `apps/studies/views.py` — `amendment_create`, and similar in `amendment_detail` / `amendment_list`.  

**Fix:** Use the same pattern everywhere (e.g. case-insensitive):

```python
is_co_i = bool(
    request.user.email
    and submission.co_investigators
    and request.user.email.lower() in submission.co_investigators.lower()
)
```

Apply in `amendment_create`, `amendment_detail`, and `amendment_list` (and any other place that checks `co_investigators`).

---

## LOW SEVERITY

### L-1. No System-Specific Salt for Participant Identity (Cross-Database Linkage)

**Risk:** For research exports or linkage to other anonymous databases, participant identity (e.g. `user.id` or `profile.student_id`) is stored in plain form. If the same identifier is used in another system, datasets could be linked. You requested a system-specific salt so hashes from this app cannot be reversed or linked to other DBs.

**Location:** No current hashing layer for export/linkage.  

**Fix:** Do not change core auth or FERPA storage. For **exports** (e.g. research datasets), add a utility that derives a stable, opaque participant ID using a system-specific salt and HMAC or keyed hash (e.g. HMAC-SHA256 with `settings.PARTICIPANT_EXPORT_SALT` from env). Example:

- Add `PARTICIPANT_EXPORT_SALT` to `env.example` and load in settings (no default in production).
- When generating export files, use `anon_id = hmac.new(settings.PARTICIPANT_EXPORT_SALT.encode(), str(participant.id).encode(), 'sha256').hexdigest()[:32]` (or similar) and export `anon_id` instead of internal IDs. Document that this salt is system-specific and must not be shared with other systems.

---

### L-2. Course List/Detail Unauthenticated (Design Choice)

**Risk:** `course_list` and `course_detail` in `apps/courses/views.py` have no `@login_required`. Course and enrollment data may be considered FERPA-sensitive depending on policy.

**Fix:** If policy requires it, protect with `@login_required` and scope `course_detail` so participants only see their own enrollment (you already scope enrollment by `request.user` when authenticated). If public course list is intentional, document the decision and ensure no PII is shown to anonymous users.

---

### L-3. Audit Logs Missing IP / User-Agent

**Risk:** `AuditLog` has `ip_address` and `user_agent` fields but signals do not set them; only the request has that information. For 45 CFR 46 and security investigations, IP/user-agent are valuable.

**Fix:** Where audit events are created from a view (e.g. future consent or credit logs), pass `request.META.get('REMOTE_ADDR')` and `request.META.get('HTTP_USER_AGENT', '')` into `AuditLog`. For signal-based logs, you can attach the current request (e.g. via middleware or thread-local) only if you do so carefully and document it; otherwise leave signal-created logs without IP and ensure view-created critical actions (e.g. credit grant, protocol decision) include IP/user-agent.

---

### L-4. Reporting CSV Exposes FERPA Data (Expected with Access Control)

**Note:** `course_credits_csv` correctly restricts to `course.instructor == request.user` or admin and uses UUID for `course_id`. The CSV contains Student ID, Name, Email — FERPA data. This is expected for instructor use; ensure access control remains strict and that only necessary roles (instructor/admin) can hit this endpoint. No code change required if policy is documented; consider logging access to this view for audit.

---

## Summary Table

| ID   | Severity | Category           | One-line description |
|------|----------|--------------------|----------------------|
| H-1  | High     | Auth/RBAC          | Registration accepts client-supplied role → privilege escalation |
| H-2  | High     | OWASP CSRF         | submit_response is csrf_exempt |
| H-3  | High     | OWASP IDOR         | mark_attendance exposes other participants’ PII |
| H-4  | High     | Auth/Data integrity | Unauthenticated protocol submission for any study |
| M-1  | Medium   | Secrets            | SECRET_KEY has insecure default |
| M-2  | Medium   | IRB audit          | Consent and credit grant not in AuditLog |
| M-3  | Medium   | OWASP XSS          | Messages rendered with \|safe |
| M-4  | Medium   | RBAC consistency   | Co-I check case-sensitivity |
| L-1  | Low      | Data separation    | No system-specific salt for export hashing |
| L-2  | Low      | FERPA              | Course list/detail unauthenticated (design) |
| L-3  | Low      | Audit              | AuditLog IP/user_agent not set in signals |
| L-4  | Low      | FERPA              | CSV export access (document/log) |

---

*After applying these fixes, use the accompanying IT Executive Summary for the University CIO.*
