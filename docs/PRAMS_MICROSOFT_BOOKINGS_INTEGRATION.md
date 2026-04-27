# PRAMS × Microsoft Bookings Integration — Methodological Guide

**Status: Not in use.** Microsoft Bookings is not being used for study scheduling. For calendar-based scheduling that works with the student sign-up system, see **[Google Calendar integration](GOOGLE_CALENDAR_INTEGRATION.md)** instead.

---

This document outlines a **methodical approach** to integrating Microsoft Bookings (available to all Nicholls students) with PRAMS while preserving **FERPA compliance**: PRAMS must never collect, store, or process name, email, or other PII.

---

## 1. Goals and Constraints

| Goal | Notes |
|------|--------|
| Use Bookings for scheduling UX | Students already have access; familiar calendar, reminders, Teams/Outlook integration. |
| Keep PRAMS FERPA-compliant | PRAMS stores only **Secure Participant ID** and **cancellation PIN**. No name, email, or user_id. |
| Single source of truth for “who’s signed up” | PRAMS remains the system of record for study signups and capacity. |
| Optional: cancellations in Bookings → PRAMS | If a student cancels in Bookings, PRAMS should free the slot (using Secure ID + PIN or a server-to-server link). |

**Constraints**

- PII (name, email) may exist **only in the Microsoft 365 tenant** (Bookings/Outlook). It must **not** be sent to or stored in PRAMS.
- PRAMS APIs accept only `study_id`, `participant_secure_id`, and (for cancel) `cancellation_pin`.

---

## 2. Integration Patterns

Three high-level patterns:

| Pattern | Description | Pros | Cons |
|--------|-------------|------|------|
| **A. Bookings-led** | Student books in Bookings; a flow sends only Secure ID (and study mapping) to PRAMS. | Uses Bookings UX and calendar; no PII in PRAMS. | Requires mapping Bookings services/slots to PRAMS studies; flow must handle capacity. |
| **B. PRAMS-led** | Student signs up in PRAMS only; optionally we push an event to Bookings/Outlook via Graph. | PRAMS stays single source of truth; no PII in PRAMS. | We’d need to create “anonymous” or system calendar events; Bookings might not be the right consumer. |
| **C. Hybrid (two entry points)** | Both: students can book via **Bookings** (flow → PRAMS) or via **PRAMS catalog** (existing flow). | Flexibility; Bookings for those who prefer it. | Two paths to maintain; need to avoid double-booking (same Secure ID in both). |

**Recommended:** **A (Bookings-led)** or **C (Hybrid)**. Use **Bookings-led** if you want “all signups go through Bookings.” Use **Hybrid** if you want to keep the current PRAMS catalog and add Bookings as an alternative.

---

## 3. Recommended Architecture: Bookings-Led with Power Automate

### 3.1 Data flow (no PII to PRAMS)

1. **Microsoft Bookings**
   - One **Booking business** (e.g. “Nicholls Research Studies”) with one or more **services** (e.g. “Study: Survey on X,” “Study: Lab Session Y”).
   - Each service has a **required custom question**: e.g. **“Secure Participant ID”** (free text). This is the only identifier PRAMS will see.
   - Optional: second custom question or service notes to carry a **PRAMS study ID** (if one Bookings service is used for multiple studies), or use one Bookings service per PRAMS study.

2. **Student books**
   - Student opens the Bookings page, picks a service and slot, enters name/email (for Bookings/Outlook only) and the **Secure Participant ID** in the custom question.
   - Bookings sends confirmation/calendar invite as usual (Microsoft only; no PII to PRAMS).

3. **Power Automate**
   - Trigger: **When an appointment is created** (Bookings connector).
   - Trigger output includes **CustomQuestionAnswers** with the **Answer** for “Secure Participant ID.”
   - Trigger also provides **ServiceId**, **StartTime**, **SelfServiceAppointmentId**, etc.
   - Flow logic:
     - **Mapping:** Resolve **Bookings ServiceId** (and optionally slot/time) → **PRAMS study_id** (see Section 4).
     - **Call PRAMS:** HTTP POST to `POST /api/signup/` with body:
       - `study_id`: from mapping.
       - `participant_secure_id`: from CustomQuestionAnswers (the Secure Participant ID answer).
     - If PRAMS returns **409** (no slots / already signed up), flow can:
       - Send a custom message to the Bookings admin and/or try to cancel the Bookings appointment via Graph/connector (optional).
     - If PRAMS returns **201**, body includes **cancellation_pin**.
   - **Optional:** Include the **cancellation_pin** in a follow-up (e.g. add to appointment notes via Graph, or send a separate notification). If you do, do **not** send PII to PRAMS; only PIN + instructions (e.g. “Use this PIN with your Secure ID to cancel in PRAMS”).

4. **PRAMS**
   - Receives only `study_id` and `participant_secure_id`; creates signup; returns `cancellation_pin` and study details. No name/email ever stored.

5. **Cancellation**
   - **Option A (student cancels in Bookings):** Flow **When an appointment is cancelled** → call PRAMS `DELETE /api/signup/` with `study_id`, `participant_secure_id`, and `cancellation_pin`. The flow must **store** the PIN somewhere when it was received (e.g. in Bookings appointment notes or a small store). See Section 5.
   - **Option B (student cancels in PRAMS):** Use existing PRAMS cancel flow (Secure ID + PIN); optionally use Graph to cancel the corresponding Bookings appointment if you have a stable link (e.g. by storing `selfServiceAppointmentId` in PRAMS when you first create the signup from the flow—see optional extension below).

---

## 4. Mapping Bookings → PRAMS

PRAMS identifies studies by **study_id** (UUID). Bookings uses **ServiceId** and optionally date/time.

**Option 1 — One Bookings service per PRAMS study (simplest)**  
- Create one Bookings “service” per PRAMS study.  
- Maintain a **mapping** (e.g. in Power Automate: “Switch” or lookup table): `Bookings ServiceId` → `PRAMS study_id`.  
- Flow uses **ServiceId** from the trigger to get **study_id** and call PRAMS.

**Option 2 — One Bookings service, many PRAMS studies**  
- Use a second custom question “PRAMS Study ID” and have the student paste the study UUID, or use a dropdown (less user-friendly).  
- Or encode study in the slot (e.g. different staff = different study) and map (StaffId / slot) → study_id in the flow.  
- More complex; Option 1 is usually better.

**Option 3 — Store mapping in PRAMS (future)**  
- Add an optional field on **PRAMSStudy**: e.g. `bookings_service_id` (and optionally `bookings_business_smtp`).  
- Expose e.g. `GET /api/studies/?bookings_service_id=...` or include `bookings_service_id` in `GET /api/studies/` so the flow can resolve **study_id** from **ServiceId** without hardcoding in the flow.

---

## 5. Handling Cancellation PIN When Bookings Leads

When the flow calls `POST /api/signup/`, PRAMS returns **cancellation_pin**. The student needs this to cancel in PRAMS. They may also cancel from Bookings; then the flow should call `DELETE /api/signup/`.

**Ways to get the PIN into the flow later:**

1. **Store in Bookings appointment**  
   - After PRAMS returns 201, use **Microsoft Graph** to update the booking appointment’s **notes** or an extended property with the PIN (and a short instruction: “Use with your Secure ID to cancel in PRAMS”).  
   - When “When an appointment is cancelled” runs, the flow can read the same appointment (before it’s fully removed) or keep the PIN in a small store keyed by `SelfServiceAppointmentId` or customer email (stored only in Microsoft, not in PRAMS).

2. **Send PIN only by email (from Bookings)**  
   - Don’t store PIN in PRAMS for later flow use. When the flow gets 201, send an email (via Office 365 connector) to the customer with the PIN and instructions.  
   - If they cancel in Bookings, the flow **cannot** call PRAMS DELETE unless you have another way to identify the signup (e.g. by `participant_secure_id` + `study_id` and then you’d need the PIN from somewhere—e.g. a secure store keyed by appointment ID).

3. **Store PIN in a small external store (e.g. SharePoint list or Azure Table)**  
   - Key: `SelfServiceAppointmentId` or a hash of (study_id + participant_secure_id).  
   - Value: `cancellation_pin`.  
   - On “appointment cancelled,” flow looks up PIN and calls `DELETE /api/signup/`.  
   - PII (name/email) still only in Microsoft; the store holds only IDs and PIN.

---

## 6. Implementation Checklist (Bookings-Led)

- [ ] Create (or choose) a **Bookings business** (e.g. Nicholls Research Studies).
- [ ] For each PRAMS study (or a subset), create a **Bookings service** with the same title/description and appropriate duration.
- [ ] Add a **required custom question**: “Secure Participant ID” (or exact wording your students see).
- [ ] Decide **mapping** Bookings ServiceId → PRAMS study_id (flow Switch/lookup or future PRAMS field).
- [ ] In **Power Automate** (as Bookings admin):
  - Create flow: trigger **When an appointment is created** for that Bookings mailbox.
  - Parse **CustomQuestionAnswers** for the Secure Participant ID answer.
  - Resolve **ServiceId** → **study_id**.
  - **HTTP** action: POST to `https://<your-prams-domain>/api/signup/` with body `{ "study_id": "<uuid>", "participant_secure_id": "<from CustomQuestionAnswers>" }`.
  - If 201: optionally store PIN (appointment notes / email / external store) and add instructions for cancellation.
  - If 409: optionally notify admin and/or cancel the Bookings appointment.
- [ ] (Optional) Flow: **When an appointment is cancelled** → look up PIN (from notes/store) → **HTTP** DELETE to `/api/signup/` with `study_id`, `participant_secure_id`, `cancellation_pin`.
- [ ] Document for students: “Use your Secure Participant ID when booking; save the PIN we send you to cancel in PRAMS or cancel from this Bookings page.”

---

## 7. FERPA Boundary Summary

| System | May hold | Must not send to PRAMS |
|--------|----------|-------------------------|
| **Microsoft Bookings / Outlook** | Name, email, phone, custom answers (including Secure ID) | — |
| **Power Automate** | Secure Participant ID, study_id, cancellation_pin, ServiceId, appointment IDs | Do not send name/email to PRAMS or to any external system that stores them with the signup. |
| **PRAMS** | study_id, participant_secure_id, cancellation_pin only | Name, email, user_id, or any PII. |

By design, **only the Secure Participant ID and PIN** (and study/signup identifiers) cross into PRAMS. Student identity stays in the Microsoft 365 tenant.

---

## 8. PRAMS API Support for Bookings Mapping (Implemented)

PRAMS supports mapping Bookings services to studies without hardcoding in the flow:

- **PRAMSStudy** has an optional field **`bookings_service_id`** (string). Set it in Django admin to the Microsoft Bookings **ServiceId** for that study.
- **GET /api/studies/** returns each study with **`bookings_service_id`** in the JSON (or `null` if unset).
- The Power Automate flow can: call `GET /api/studies/`, find the study where `bookings_service_id` equals the trigger’s **ServiceId**, then use that study’s **`id`** in `POST /api/signup/`.

This keeps the mapping in one place (PRAMS admin) and avoids maintaining a separate lookup in Power Automate.

---

## 9. References

- [Microsoft Bookings API (Graph)](https://learn.microsoft.com/en-us/graph/api/resources/booking-api-overview)
- [Add custom questions to the booking page](https://learn.microsoft.com/en-us/microsoft-365/bookings/add-questions)
- [Power Automate + Bookings](https://learn.microsoft.com/en-us/microsoft-365/bookings/power-automate-integration)
- [Bookings connector — AppointmentData includes CustomQuestionAnswers](https://learn.microsoft.com/en-us/connectors/microsoftbookings/)
