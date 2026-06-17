# Anonymous Timeslot Booking — Security & Compliance

**Audience:** IT security review, IRB, FERPA compliance  
**Feature:** Public sign-up without participant accounts (`Study.allows_anonymous_booking`)

---

## 1. Data classification

| Stored | FERPA education record? | Notes |
|--------|-------------------------|-------|
| `AnonymousSignup` rows | **No** | No name, email, student ID, or `User` FK |
| Booking reference (UUID) | **No** | Opaque token for cancellation only |
| Cancellation PIN | **No** | 4-digit secret; not linked to institutional identity |
| Researcher notification email | **No student PII** | Study title, slot time, location, capacity only |
| `.ics` download | **No PII** | Study title, time, location |

Anonymous booking is intended for **voluntary research participation without credit** (e.g. goal-setting lab), aligned with `FEDERAL_AUDIT_SURVIVAL_NO_CREDIT.md`.

---

## 2. Threat controls

| Threat | Control |
|--------|---------|
| **CSRF** | Django CSRF middleware; all POST forms include `{% csrf_token %}` |
| **Slot flooding / abuse** | IP rate limit on book (`ANONYMOUS_BOOKING_RATE_LIMIT_BOOK`, default 5/hour) |
| **PIN brute force** | IP rate limit on cancel (`ANONYMOUS_BOOKING_RATE_LIMIT_CANCEL`, default 15/15 min); constant-time PIN compare; generic error message |
| **IDOR (success page)** | Confirmation shown only via one-time session key (`anonymous_booking_id`), not a public URL |
| **IDOR (roster)** | Researcher roster requires login + study ownership |
| **IDOR (.ics)** | Only for `active_approved` studies with `allows_anonymous_booking` |
| **Enumeration** | Cancel failures use one message: “Booking not found or PIN invalid.” |
| **Concurrency / overbooking** | `select_for_update()` + capacity check in atomic transaction |
| **IRB gating** | Only `Study.active_approved` studies accept anonymous booking |
| **Audit (45 CFR 46)** | `AuditLog` entries for signup and cancel with IP/user-agent (no student PII) |
| **Transport** | Production: HTTPS, secure cookies (`config/settings.py`) |

---

## 3. Configuration (environment)

Optional overrides in `.env`:

```bash
ANONYMOUS_BOOKING_RATE_LIMIT_BOOK=5
ANONYMOUS_BOOKING_RATE_LIMIT_BOOK_WINDOW=3600
ANONYMOUS_BOOKING_RATE_LIMIT_CANCEL=15
ANONYMOUS_BOOKING_RATE_LIMIT_CANCEL_WINDOW=900
```

Reverse-proxy rate limiting (e.g. campus WAF) is recommended as a defense-in-depth layer.

---

## 4. Operational notes

- Researchers enable **Allow anonymous sign-up** per study; credit-based studies remain on authenticated flow.
- Cancellation PINs are shown once on the confirmation screen; students must save them.
- Django admin lists anonymous signups without exposing PINs in list views.
- Email to researchers requires `EMAIL_HOST`; skipped gracefully when unset.

---

## 5. Residual risk (accepted)

- **4-digit PIN entropy:** Mitigated by rate limits and short-lived booking window; not used for authentication to institutional systems.
- **Shared lab machines:** Session-based confirmation may be visible on a shared browser; students should complete flow on a private device or record reference/PIN immediately.

---

*Cross-reference: `SECURITY_COMPLIANCE_REMEDIATION_LIST.md`, `IT_EXECUTIVE_COMPLIANCE_SUMMARY.md`, `FERPA_AUDIT_REPORT.md`.*
