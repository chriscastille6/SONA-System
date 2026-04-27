# PRAMS Server Error Audit

**Scope:** Views and API handlers across the PRAMS (Participant Recruitment and Management System) codebase.  
**Goal:** Identify paths that can raise unhandled exceptions and result in HTTP 500 responses.

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **High**  | 4 | Unhandled exception leads to 500 in common or API paths |
| **Medium** | 3 | Unhandled exception in authenticated or edge-case paths |
| **Low**   | 2 | File/JSON read could fail; or minor edge cases |

---

## High severity

### 1. `protocol_submission_list` – backfill loop (studies/views.py)

**Location:** ~lines 1648–1651.

**Issue:** Iterates over submission IDs and calls `ProtocolSubmission.objects.get(id=sub_id)`. If a submission is deleted between the filter and the `get` (e.g. by another request or admin), `ProtocolSubmission.DoesNotExist` is raised and the whole page returns 500.

**Fix:** Wrap the get/save in `try/except ProtocolSubmission.DoesNotExist` and skip missing IDs (or use `filter(pk=sub_id).first()` and only call `save()` if not None).

---

### 2. `submit_response` – API (studies/views.py)

**Location:** ~lines 653–676.

**Issue:** `Response.objects.create(...)` is not wrapped in try/except. Database errors (e.g. constraint violation, connection failure) surface as 500. This is a public-facing API used for protocol response submission.

**Fix:** Wrap the create (and optional `run_sequential_bayes_monitoring.delay`) in try/except; on failure return a structured JSON error (e.g. 503 or 500 with `{"error": "..."}`) and log the exception.

---

### 3. `submit_infographic_email` – API (studies/views.py)

**Location:** ~lines 696–718.

**Issue:** `StudyEmailContact.objects.create(...)` can raise on DB error (e.g. duplicate constraint if added later, or connection failure), resulting in 500.

**Fix:** Same as above: try/except around create, return JSON error and log.

---

### 4. `course_credits_csv` – reporting (reporting/views.py)

**Location:** ~lines 46–58, loop over enrollments.

**Issue:** Uses `enrollment.participant.profile.student_id`. If a participant has no `Profile` (e.g. profile creation signal failed or legacy user), `RelatedObjectDoesNotExist` is raised and the CSV export returns 500.

**Fix:** Use `getattr(enrollment.participant, 'profile', None)` and then `getattr(profile, 'student_id', None) or 'N/A'`, or handle `Profile.DoesNotExist` in a try/except for that row.

---

## Medium severity

### 5. `protocol_vignettes` – file + JSON (studies/views.py)

**Location:** ~lines 436–439.

**Issue:** `open(vignettes_path)` can raise `IOError`/`OSError`; `json.load(f)` can raise `json.JSONDecodeError`. Both are unhandled and would 500.

**Fix:** Try/except around file open and `json.load`; on failure raise `Http404("Vignette pool unavailable.")` or return a short error message after logging.

---

### 6. `extam4_summary_html` – file read (studies/views.py)

**Location:** ~lines 55–59.

**Issue:** `open(path, "r", encoding="utf-8")` can raise `IOError`/`OSError` (e.g. permissions, missing file after deploy). Currently only `path.exists()` is checked; race condition or filesystem issue can still cause 500.

**Fix:** Wrap the open/read in try/except; on failure re-raise `Http404` or log and raise `Http404("Summary not available.")`.

---

### 7. `protocol_study_documentation` – file read (studies/views.py)

**Location:** ~lines 452–453.

**Issue:** `open(path, ...)` and `f.read()` can raise `IOError`/`OSError`. Unhandled → 500.

**Fix:** Same pattern: try/except around open/read; on failure `Http404("Documentation not available.")` and log.

---

## Low severity

### 8. `study_status` – POST create (studies/views.py)

**Location:** ~lines 464–469, 766.

**Issue:** `StudyUpdate.objects.create(..., attachment=attachment)` can fail on storage or DB error (e.g. file too large, disk full). Unhandled → 500.

**Fix:** Wrap in try/except; on failure set `update_form_error` and re-render the form with a user-visible message.

---

### 9. `irb_review_create` – file upload + create (studies/views.py)

**Location:** ~lines 523–541.

**Issue:** `ReviewDocument.objects.create(...)` in a loop and `review.save(update_fields=['uploaded_files'])` can raise (e.g. storage, DB). Unhandled → 500.

**Fix:** Wrap the entire POST block in try/except; on failure add a message and re-render the form (or redirect back with error).

---

## Already handled well

- **studies:** `protocol_submit` – POST wrapped in try/except, logs and redirects with message.  
- **studies:** `hr_sjt_student_data_consent` – `update_or_create` wrapped in try/except, re-renders with error.  
- **studies:** `protocol_submission_detail` – `submission.study` access wrapped in try/except for deleted study.  
- **accounts:** `register` – `create_user` / token create in try/except, user-facing error message.  
- **prescreening:** `submit_prescreen` – uses `update_or_create`; `request.user.prescreen_response` wrapped in `PrescreenResponse.DoesNotExist`.  
- **studies:** `submit_response` – `json.loads(request.body)` already wrapped; returns 400 on invalid JSON.

---

## Recommendations

1. **Apply fixes for High items (1–4)** so that list page, both APIs, and CSV export do not 500 on the identified edge cases.
2. **Harden file/JSON reads (5–7)** so missing/corrupt assets return 404 or a clear error instead of 500.
3. **Optionally harden study update and IRB review create (8–9)** with try/except and user-visible error messages.
4. **Monitoring:** Ensure 500s are logged (e.g. Django logging, Sentry) so any remaining or new failure paths are visible in production.

---

*Audit date: March 2025*
