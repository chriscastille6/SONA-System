# SONA Replacement System — IT Security & Compliance Executive Summary

**To:** University CIO / IT Leadership  
**From:** [Lead Architect]  
**Re:** Pre–IT review security and compliance posture  
**Date:** February 2026  

---

## 1. System Overview

The system is a custom, internal web application that replaces SONA for **federal IRB compliance tracking** and **student participation for course credit**. It processes **FERPA-protected education records** and is designed for hosting on an **internal IT-managed VM** with future **campus SSO integration**. The stack is Django (Python), PostgreSQL, and standard web security middleware (HTTPS, CSRF, session auth).

---

## 2. Security Architecture

- **Authentication:** Django session-based authentication; password hashing via Argon2/PBKDF2 (NIST-aligned). No credentials stored in code; login/logout and password reset use framework flows.
- **Authorization (RBAC):** Roles — Administrator, IRB Member, Researcher, Instructor, Participant — are enforced at the **view layer** on every sensitive route. Object-level checks ensure researchers see only their studies, participants only their bookings/credits, and IRB members only assigned protocols. Admin/staff have elevated access under controlled paths.
- **Secrets:** All secrets (SECRET_KEY, database URL, email credentials, API keys, optional participant-export salt) are read from **environment variables** (e.g. `.env`). `.env` is in `.gitignore` and is not committed. Example/template (`env.example`) documents required variables without values.
- **Transport & cookies:** In production (DEBUG=False), SSL redirect, secure and HttpOnly session/CSRF cookies, HSTS, and X-Frame-Options are enabled. Configuration supports proxy headers for campus reverse proxy.

---

## 3. Threat Mitigation

| Threat | Mitigation |
|--------|------------|
| **Privilege escalation** | Self-registration restricted to Participant role; all other roles assigned by administrators or invite flows. No client-supplied role accepted for privilege roles. |
| **IDOR (access to other users’ data)** | All sensitive views resolve objects with **ownership or role scope** (e.g. `Signup` by participant or by study researcher). Unauthorized access returns 404 where appropriate to avoid information disclosure. |
| **Cross-database linkage** | For research exports, a **system-specific salt** (from environment) is used to derive opaque participant identifiers so hashes from this system cannot be reversed or linked to other anonymous research databases. |
| **CSRF** | Django CSRF middleware enabled; forms and state-changing requests use CSRF tokens. Protocol submission API uses token-based or same-origin submission (no blanket CSRF exemption). |
| **SQL injection** | ORM used throughout; no raw SQL with user input. Management scripts that use raw SQL use parameterized or controlled inputs. |
| **XSS** | User-supplied content is escaped in templates; message display avoids unsafe HTML unless strictly controlled/sanitized. |

---

## 4. Audit & IRB Alignment (45 CFR 46)

- **Immutable(ish) audit trail:** Critical actions are written to a dedicated **AuditLog** table (append-only in practice): study creation, IRB status changes, study approval/deactivation. Who approved a study and when is also recorded on the Study and ProtocolSubmission models.
- **Consent and credit:** Participant consent timestamp is stored on signup records; credit grants are recorded in CreditTransaction. Audit logging has been extended to include **participant consent** and **credit grant** events for IRB and compliance review.
- **Logging:** Application and error logging go to files and console; log directory is local and not exposed via the web server.

---

## 5. SSO Readiness

- The application uses Django’s built-in authentication and is structured to **swap the authentication backend** for a SAML/OAuth2/OIDC backend (e.g. django-saml2, django-allauth, or institutional SSO middleware) without changing authorization logic. RBAC and object-level checks are in the view layer and remain valid once the user identity is provided by SSO. Session handling (secure cookies, timeout) will align with institutional SSO and IT policies at integration time.

---

## 6. Remediation Applied

The following were addressed in code and configuration:

- **H-1:** Registration no longer accepts client-supplied role; self-registration is Participant-only.
- **H-2:** Protocol response endpoint no longer uses CSRF exemption; same-origin requests require CSRF token.
- **H-3:** Mark-attendance enforces authorization before rendering; unauthorized users receive 404 to prevent PII disclosure.
- **H-4:** Protocol submission restricted to active, approved studies only; unapproved/inactive return 403.
- **M-1:** SECRET_KEY is required in production (no fallback default when DEBUG is False).
- **M-2:** Audit trail extended to participant consent (Signup created) and credit-grant (CreditTransaction created) events.
- **M-3:** Message display uses auto-escape; format_html removed from user-facing messages.
- **M-4:** Co-investigator checks use case-insensitive comparison consistently.
- **L-1:** System-specific salt (PARTICIPANT_EXPORT_SALT) and export utility for anonymized participant IDs.
- **L-2:** Course list and detail require authentication.
- **L-3:** Signal-based audit logs documented; view-created logs can include IP/user-agent.
- **L-4:** Course credits CSV access logged for audit; FERPA data access restricted to instructor/admin.

---

## 7. Conclusion

The system’s security architecture is designed to meet **Tier-1/Tier-2** expectations and **FERPA** handling for education records. Role-based access is enforced on backend routes; IDOR risk is mitigated by scoped object access and 404-for-unauthorized behavior; system-specific salting supports research data separation; and audit logging supports IRB (45 CFR 46) requirements. With the remediations above applied, the system is in a **ready state for internal IT security review** and for planning **internal SSO integration**.

---

*Supporting technical details and prior findings are in `SECURITY_COMPLIANCE_REMEDIATION_LIST.md`.*
