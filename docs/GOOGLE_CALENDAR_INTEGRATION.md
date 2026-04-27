# Google Calendar × Study Sign-Up Integration

Use **Google Calendar** for scheduling study sessions (when, where, which faculty/room) while keeping **SONA as the single source of truth** for student sign-ups, capacity, and reminders.

---

## 1. Goals

| Goal | How |
|------|-----|
| Assign faculty and rooms to study sessions | Create calendar events (or a shared calendar) for each timeslot; optional: store event ID on `Timeslot` for updates. |
| Keep sign-up counts accurate | Students sign up only in SONA (studies app). No booking in Google Calendar; Calendar is for team visibility. |
| Keep sending reminders | Use existing SONA reminder tasks (24h and 2h emails). No change to reminder logic. |

**Principle:** SONA owns *who is signed up* and *reminders*. Google Calendar is for *when/where/who’s running the study*.

---

## 2. Integration Patterns

### A. One-way sync: SONA → Google Calendar (recommended)

- When a **timeslot** is created or updated in SONA, create or update a **Google Calendar event** (e.g. on a shared “Research studies” calendar).
- Event title: e.g. `Study: <study title>` or `[Study] <study title> — <faculty name>`.
- Event time: `timeslot.starts_at` / `timeslot.ends_at`.
- Event location: `timeslot.location` (room from CBA availability or manual).
- Optional description: capacity, sign-up count, link to SONA manage page.
- **Students do not book via Calendar.** They sign up in SONA as they do now. Reminders stay in SONA (`send_24h_reminders`, `send_2h_reminders`).

**Benefits:** Research team sees all study sessions on one calendar; faculty/room assignment is visible; no double-booking of rooms if you use the same calendar for availability. Sign-up totals and reminders remain entirely in SONA.

### B. Calendar for visibility only (manual or batch)

- No automatic sync. Periodically (e.g. script or admin action) create/update Google Calendar events from SONA timeslots.
- Same idea as A: events show study name, time, location, optional faculty. Students still sign up in SONA; reminders unchanged.

### C. Calendar as source of “slots” (advanced)

- Create study sessions in Google Calendar first; an integration (e.g. nightly job or API) creates/updates SONA timeslots from Calendar events.
- SONA still owns sign-ups and reminders; Calendar would own “when we offer slots.” More moving parts; only consider if you need to drive slot creation from Calendar.

**Recommendation:** Start with **A** (one-way SONA → Calendar) so you get a single place to see study sessions and room/faculty without changing sign-up or reminders.

---

## 3. Keeping Sign-Up Counts and Reminders in SONA

- **Sign-ups:** All booking happens in the studies app (e.g. `book_timeslot`). `Signup` and `Timeslot.current_signups` / `available_capacity` stay the source of truth.
- **Reminders:** Existing Celery tasks `send_24h_reminders` and `send_2h_reminders` use `Signup` and `Timeslot`; they send email to `participant.email`. No change needed; nothing moves to Google for reminders.
- **Google Calendar** is not used for:
  - Student booking
  - Sending reminders
  - Storing participant identity or counts

So: **overall number of sign-ups** and **reminders** stay fully in SONA; Google Calendar is only for displaying and managing *when/where/who* for the research team.

---

## 4. Implementation Outline (One-Way SONA → Google Calendar)

1. **Google Cloud**
   - Create a project (or use existing).
   - Enable **Google Calendar API**.
   - Create a **service account** (or OAuth client) with access to the target calendar (e.g. shared “Research studies” calendar). Share the calendar with the service account’s email (e.g. `...@....iam.gserviceaccount.com`) as “Make changes to events.”

2. **SONA**
   - Store Calendar API credentials (e.g. service account JSON) in env or Django settings; never commit secrets.
   - Optional: add a field on `Timeslot` such as `google_calendar_event_id` (and optionally `google_calendar_id`) to update/delete the same event when the timeslot changes or is cancelled.

3. **Sync logic**
   - **On timeslot create:** Call Calendar API to create an event (title, start/end, location, optional description with capacity/sign-up link). Save `event_id` on `Timeslot` if you want updates.
   - **On timeslot update:** If `google_calendar_event_id` is set, PATCH the event (time, location, title).
   - **On timeslot delete/cancel:** If `google_calendar_event_id` is set, delete (or mark cancelled) the event.
   - Optionally: a management command or Celery task that syncs all active timeslots to the calendar (create or update by ID).

4. **Faculty/room**
   - You already have CBA availability (rooms, faculty windows). When creating a timeslot in SONA, set `location` (and optional notes). The same `location` (and any faculty in the event title or description) can be sent to the Calendar event so the team sees who’s running which session and where.

5. **Reminders**
   - Do **not** rely on Google Calendar attendee reminders for participants. Keep using SONA’s email reminders so sign-up and reminder logic stay in one place and you keep full control over wording and tracking (`reminder_24h_sent`, `reminder_2h_sent`).

---

## 5. FERPA / PRAMS Note

For **PRAMS** (FERPA-compliant, no PII): students still sign up with Secure Participant ID only; reminders might be sent to a non-PII channel if you add one (e.g. reminder link they get when they sign up). Google Calendar events for PRAMS studies should **not** contain participant names or identifiers—only study title, time, location, faculty/room. Same principle: Calendar is for scheduling visibility; sign-ups and reminders stay in PRAMS/SONA.

---

## 6. Summary

| Concern | Approach |
|--------|----------|
| Assign faculty/room to run the study | Use Google Calendar events (and optionally SONA `Timeslot.location` / notes) so the team sees who and where. |
| Integrate with student sign-up | Students sign up in SONA only; no sign-up in Calendar. Optional: one-way sync SONA → Calendar so sessions appear on a shared calendar. |
| Track overall sign-up numbers | All in SONA: `Timeslot`, `Signup`, capacity and counts. |
| Send reminders | Keep using SONA reminder tasks; no change. |
| Microsoft Bookings | Not in use; Google Calendar is the recommended calendar integration. |

By keeping sign-ups and reminders in SONA and using Google Calendar only for session visibility and faculty/room assignment, you get a single place to see when/where studies run while still keeping full control over counts and reminders.
