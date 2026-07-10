# PRAMS — One-Page Summary for Deans & Department Heads

**Nicholls State University · July 2026 ·** [Full guide](DEAN_AND_CHAIR_GUIDE.md)

---

## What it is

**PRAMS** = Nicholls-built **research participation system** (SONA replacement). Faculty use it to **recruit IRB-approved study participants**, **host web-based protocols** on **bayoupal**, and **track compliance**. Not a gradebook. Not a student AI tool.

---

## Why leadership cares (and why you shouldn’t panic)

| Concern | Reality for PRAMS |
|---------|-------------------|
| FERPA / student privacy | Default: **voluntary research, no course credit** → smaller privacy scope |
| Louisiana AI executive orders | **Nicholls-hosted**; **no DeepSeek** or banned foreign AI |
| News (SNHU, etc.) | Those cases = **advertising trackers on student portals** — not this system |
| Shadow IT | Code reviewed via **bayouops GitLab + IT** before production |

**One-line story:** *IT-reviewed, Louisiana-hosted faculty research infrastructure — not professors running ChatGPT on students.*

---

## How it works (simple)

**Three kinds of student-related data** (see [STUDENT_DATA_TAXONOMY.md](STUDENT_DATA_TAXONOMY.md)):

| Tier | What | PRAMS example |
|------|------|---------------|
| **I — Student-generated** | What they wrote/said (may or may not include PII) | Essay or survey in protocol |
| **II — Student-linked** | Clearly tied to identity | Signup roster, student ID, credit |
| **III — Synthetic / de-identified** | Real content **without** identity link, or fake demo data | Anonymous `Response` DB; synthetic demos |

```
Faculty protocol → PRAMS (bayoupal) → Student signs up (Tier II roster) → Anonymous response store (Tier I, no name link)
```

| Old (SONA / ad hoc) | PRAMS |
|---------------------|-------|
| Paid vendor or random survey site | **Nicholls server** |
| Protocol hosted elsewhere | **Your protocol on bayoupal** |
| Spreadsheet tracking | Signup + consent + audit trail |

---

## AI — what chairs should tell faculty

See [FERPA_VIOLATION_PATHS.md](FERPA_VIOLATION_PATHS.md) for **what counts as a technical violation** (LLM + database diagrams).

| | |
|-|-|
| Students use AI in PRAMS? | **No** |
| Data sent to ChatGPT? | **No** (normal operation) |
| AI used to build it? | Dev tools only — **no real student data** in that process |
| Optional admin AI? | IRB text review only — **on our server or OFF** |

**Faculty rule:** Never put rosters, grades, or student IDs into any AI tool.

---

## Default settings (recommended)

- **Course credit:** OFF (voluntary participation only)
- **Production AI:** OFF until Nicholls AI policy exists
- **Hosting:** bayoupal.nicholls.edu only
- **Research data:** Anonymous by design (`session_id`, not student name)

---

## Dean / chair — do this

1. Know the accurate story (this page)
2. Ensure faculty still go through **IRB**
3. Don’t enable course credit without Registrar + IRB conversation
4. Direct tech questions to project lead + IT — not hallway speculation

---

## 15-second script

> PRAMS is our Nicholls-hosted SONA replacement. Protocols and anonymous research data live on bayoupal. IT reviews it through bayouops. Not a ChatGPT thing.

---

## Who to contact

| | |
|-|-|
| Faculty onboarding | Dr. Castille (project lead) |
| IT / bayouops | Nicholls IT |
| IRB | Institutional IRB |
| More detail | [DEAN_AND_CHAIR_GUIDE.md](DEAN_AND_CHAIR_GUIDE.md) |

---

*Forward subject line: **FYI: PRAMS — Nicholls research system (IT-reviewed, not an AI student tool)***
