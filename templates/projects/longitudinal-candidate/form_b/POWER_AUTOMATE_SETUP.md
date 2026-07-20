# Form B — Microsoft Power Automate nudge pipeline

**Purpose:** After Wave 1 SONA credit redirect, participants who opt in via unlinked Form B receive a scheduled Wave 2 invitation and one 72-hour friendly nudge. The contact store contains **zero** survey answers and **zero** CANDIDATE IDs.

**Environment:** University Microsoft 365 (Forms + Excel/OneDrive + Outlook + Power Automate). No external database.

---

## 1. Microsoft Forms (Form B) field setup

Create a form titled e.g. `Study IRB-XXXX — Form B Contact (Unlinked)`.

| # | Field label | Type | Required | Notes |
|---|-------------|------|----------|-------|
| 1 | Email | Text / Email | Yes | Only identifier allowed |
| 2 | I agree to receive one Wave 2 invitation and at most one friendly nudge | Choice: Yes / No | Yes | Gate the flow on Yes |
| 3 | (Display) Privacy notice | Text / Section | — | State that this form is not linked to survey answers |

**Do not add:** CANDIDATE ID, SONA `survey_code`, student ID, name, Wave 1 items.

Point participants to this Form URL from the Wave 1 completion screen (after credit redirect), or embed the link in the debrief.

---

## 2. Isolated Excel / OneDrive sheet

Create `OneDrive/Research/FormB_Contact_ONLY.xlsx` (or SharePoint site library with restricted permissions).

### Sheet: `Contacts`

| Column | Header | Description |
|--------|--------|-------------|
| A | `Email` | From Form B |
| B | `ConsentReminders` | Yes / No |
| C | `SubmittedAt` | UTC timestamp |
| D | `Wave2SendAt` | Computed schedule datetime |
| E | `NudgeSendAt` | Wave2SendAt + 72 hours |
| F | `Wave2Sent` | Yes / blank |
| G | `NudgeSent` | Yes / blank |
| H | `OptedOut` | Yes / blank |
| I | `Notes` | Optional ops notes (never survey data) |

**Hard rule:** This workbook must never contain `candidate_id`, item responses, or SONA codes.

---

## 3. Power Automate — Flow A: “Form B → store + schedule”

**Trigger:** *When a new response is submitted* (Microsoft Forms) → select Form B.

**Actions:**

1. **Get response details** (Forms) — retrieve Email + Consent.
2. **Condition:** Consent == `Yes`
   - **If no:** Terminate (or append row with `OptedOut=Yes` and skip scheduling).
   - **If yes:** continue.
3. **Compose** schedule times (example: Wave 2 launch = submitted + 14 days):

   ```
   Wave2SendAt = addDays(utcNow(), 14)
   NudgeSendAt = addHours(outputs('Wave2SendAt'), 72)
   ```

   Adjust `14` to your IRB-approved lag.

4. **Add a row into a table** (Excel Online Business) → `Contacts` table:

   - Email ← form email  
   - ConsentReminders ← Yes  
   - SubmittedAt ← `utcNow()`  
   - Wave2SendAt / NudgeSendAt ← composed values  
   - Wave2Sent / NudgeSent / OptedOut ← blank  

5. (Optional) **Send an email** confirmation: “We received your contact preference. Survey answers were not collected on this form.”

---

## 4. Power Automate — Flow B: “Wave 2 launch email”

**Trigger:** *Recurrence* (e.g., hourly) **or** *When a row is created* + Delay until `Wave2SendAt`.

Recommended pattern (robust):

1. **Recurrence:** every 1 hour.
2. **List rows present in a table** where:
   - `Wave2Sent` is blank  
   - `OptedOut` is blank  
   - `Wave2SendAt` ≤ `utcNow()`
3. **Apply to each** row:
   1. **Send an email (V2)** (Outlook) — see template below.
   2. **Update a row** → set `Wave2Sent` = `Yes`.

### Wave 2 email body (copy/paste)

**Subject:** Invitation: Wave 2 of [Study short title]

```
Hello,

You previously opted in (Form B) to receive an invitation to Wave 2 of our IRB-approved study.

Wave 2 survey link:
https://YOUR-HOST/.../wave2/index.html

This message is sent from a contact list that is kept separate from survey answers. We cannot link this email to your Wave 1 responses.

If you have already completed Wave 2, thank you—you may safely disregard this message.

To opt out of further messages, reply STOP or use: https://forms.office.com/YOUR-OPTOUT-FORM

Thank you,
[PI name], [Department], [University]
IRB protocol: IRB-XXXX-YYYY
```

---

## 5. Power Automate — Flow C: “72-hour friendly nudge”

Same structure as Flow B, filtering:

- `Wave2Sent` = Yes  
- `NudgeSent` blank  
- `OptedOut` blank  
- `NudgeSendAt` ≤ `utcNow()`

### Nudge email body

**Subject:** Friendly reminder: Wave 2 (optional)

```
Hello,

This is a single friendly reminder about Wave 2 of our study. You will not receive further automated reminders after this message.

Wave 2 survey link:
https://YOUR-HOST/.../wave2/index.html

If you have already completed Wave 2, thank you—you may safely disregard this message.

To opt out, reply STOP.

[PI name] · IRB-XXXX-YYYY
```

After send: set `NudgeSent` = `Yes`.

---

## 6. Opt-out mechanism

**Option A (simplest):** Instruct participants to reply `STOP`. Add Flow D:

1. Trigger: *When a new email arrives* (subject/body contains STOP) from shared mailbox.
2. **List rows** where Email equals sender.
3. **Update row:** `OptedOut` = `Yes`.
4. Flows B/C already skip opted-out rows.

**Option B:** Tiny second MS Form (“Unsubscribe”) with Email only → update `OptedOut`.

---

## 7. Compliance checklist (before enabling)

- [ ] Form B workbook permissions limited to PI + designated coordinator  
- [ ] No Power Automate action reads Wave 1/2 research files  
- [ ] Email templates include the exact disregard sentence for completed Wave 2  
- [ ] Only one nudge is possible (`NudgeSent` flag)  
- [ ] Synthetic test row used for dry-run (`participant.demo@example.edu`)  
- [ ] IRB protocol number visible in emails  
- [ ] Confirmed with campus M365 / IT that Forms + Automate storage is university-managed  

---

## 8. Example expression snippets

**Wave 2 time (14 days after submit):**

```
addDays(utcNow(), 14)
```

**Nudge time (72 hours after Wave 2 send time):**

```
addHours(items('Apply_to_each')?['Wave2SendAt'], 72)
```

If `Wave2SendAt` is stored as text, wrap with `formatDateTime` / `float` conversions per your Excel column types (Date/Time columns preferred).

---

## 9. Architecture (no re-identification bridge)

```
SONA ──survey_code──► Wave 1 HTML ──candidate_id + answers──► Research store A
                         │
                         └──redirect_credit.aspx (survey_code only)──► SONA credit
                         │
                         └──(optional) Form B URL──► Email store B (Excel)
                                                      │
                                                      ├── Wave 2 invite email
                                                      └── 72h nudge email
                                                             │
                                                             ▼
                                                      Wave 2 HTML ──candidate_id + answers──► Research store A
```

Stores A and B must remain unlinkable: no shared keys, no email in A, no CANDIDATE ID in B.
