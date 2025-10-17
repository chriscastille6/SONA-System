# Demo Data Structure Overview

This document visualizes how the demo data is structured and connected in the SONA system.

## 🏗️ Data Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS (15 Total)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  👨‍🔬 Researcher (1)                                               │
│     └─ Dr. Sarah Martinez (researcher@nicholls.edu)             │
│        └─ Psychology Dept, Cognitive Neuroscience Lab           │
│                                                                  │
│  👨‍🏫 Instructor (1)                                               │
│     └─ Dr. James Thompson (instructor@nicholls.edu)             │
│        └─ Psychology Dept                                       │
│                                                                  │
│  👨‍🎓 Participants (12)                                            │
│     ├─ Emily Johnson (emily.johnson@my.nicholls.edu)            │
│     ├─ Michael Brown (michael.brown@my.nicholls.edu)            │
│     ├─ Sophia Davis (sophia.davis@my.nicholls.edu)              │
│     ├─ James Wilson (james.wilson@my.nicholls.edu)              │
│     ├─ Olivia Garcia (olivia.garcia@my.nicholls.edu)            │
│     ├─ William Martinez (william.martinez@my.nicholls.edu)      │
│     ├─ Ava Rodriguez (ava.rodriguez@my.nicholls.edu)            │
│     ├─ Alexander Lee (alexander.lee@my.nicholls.edu)            │
│     ├─ Isabella Walker (isabella.walker@my.nicholls.edu)        │
│     ├─ Ethan Hall (ethan.hall@my.nicholls.edu)                  │
│     ├─ Mia Young (mia.young@my.nicholls.edu)                    │
│     └─ Daniel King (daniel.king@my.nicholls.edu)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ connected to ↓

┌─────────────────────────────────────────────────────────────────┐
│                         COURSE (1)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📚 PSYC-101 - Introduction to Psychology                        │
│     ├─ Term: 2025-Fall                                          │
│     ├─ Section: 01                                              │
│     ├─ Instructor: Dr. James Thompson                           │
│     ├─ Credits Required: 3.0                                    │
│     ├─ Status: Active                                           │
│     └─ Enrollments: 12 students                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ connected to ↓

┌─────────────────────────────────────────────────────────────────┐
│                         STUDY (1)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🔬 Decision Making Under Uncertainty                            │
│     ├─ Researcher: Dr. Sarah Martinez                           │
│     ├─ Type: In-Person Lab Study                                │
│     ├─ Location: Psychology Building, Room 215                  │
│     ├─ Duration: 30 minutes                                     │
│     ├─ Credit Value: 0.5                                        │
│     ├─ IRB Status: Approved (IRB-2025-089)                      │
│     ├─ IRB Expiration: 2026-10-15                               │
│     ├─ OSF Enabled: Yes (https://osf.io/8xk2d/)                 │
│     ├─ Bayesian Monitoring: Enabled                             │
│     ├─ BF Threshold: 10.0                                       │
│     ├─ Min Sample Size: 30                                      │
│     ├─ Max Participants: 50                                     │
│     ├─ Eligibility: Age 18+, PSYC-101 students                  │
│     └─ Status: Active & Approved                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ has ↓

┌─────────────────────────────────────────────────────────────────┐
│                       TIMESLOTS (45)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📅 Past Timeslots (~15 sessions)                                │
│     ├─ Week 1: 15 sessions (3 per day × 5 days)                 │
│     ├─ Times: 10:00 AM, 2:00 PM, 4:00 PM                        │
│     ├─ Capacity: 2 per session                                  │
│     └─ Status: Completed (with attendance records)              │
│                                                                  │
│  📅 Future Timeslots (~30 sessions)                              │
│     ├─ Week 2-3: 30 sessions                                    │
│     ├─ Times: 10:00 AM, 2:00 PM, 4:00 PM                        │
│     ├─ Capacity: 2 per session                                  │
│     └─ Status: Available (some with bookings)                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ has ↓

┌─────────────────────────────────────────────────────────────────┐
│                        SIGNUPS (23)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ Attended (12 signups)                                        │
│     ├─ Status: attended                                         │
│     ├─ Attended At: [timestamp]                                 │
│     ├─ Credits Awarded: 0.5 each                                │
│     └─ Consent Recorded: Yes                                    │
│                                                                  │
│  ❌ No-Show (2 signups)                                          │
│     ├─ Status: no_show                                          │
│     ├─ No-Show Count: Incremented                               │
│     └─ Credits Awarded: None                                    │
│                                                                  │
│  🚫 Cancelled (1 signup)                                         │
│     ├─ Status: cancelled                                        │
│     ├─ Cancelled At: [timestamp]                                │
│     └─ Credits Awarded: None                                    │
│                                                                  │
│  📝 Booked (8 signups)                                           │
│     ├─ Status: booked                                           │
│     ├─ For: Future timeslots                                    │
│     ├─ Consent Recorded: Yes                                    │
│     └─ Credits Awarded: Pending attendance                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                            ↓ generates ↓

┌─────────────────────────────────────────────────────────────────┐
│                   CREDIT TRANSACTIONS (15)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  💳 Credit Awards                                                │
│     ├─ Participant: [Student Name]                              │
│     ├─ Study: Decision Making Under Uncertainty                 │
│     ├─ Course: PSYC-101                                         │
│     ├─ Amount: +0.5 credits                                     │
│     ├─ Reason: "Completed study: [Study Title]"                 │
│     ├─ Created By: Dr. Sarah Martinez                           │
│     └─ Created At: [timestamp after attendance]                 │
│                                                                  │
│  📊 Per-Student Credits Summary:                                 │
│     ├─ Some students: 1.0 credits (attended 2 sessions)         │
│     ├─ Most students: 0.5 credits (attended 1 session)          │
│     ├─ Some students: 0.0 credits (not yet attended)            │
│     └─ Required: 3.0 credits total                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                      ↓ study also generates ↓

┌─────────────────────────────────────────────────────────────────┐
│                   PROTOCOL RESPONSES (12)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 Response Data Structure (per response):                      │
│                                                                  │
│  {                                                               │
│    "participant_id": "P001",                                     │
│    "demographics": {                                             │
│      "age": 19,                                                  │
│      "gender": "F",                                              │
│      "major": "Psychology"                                       │
│    },                                                            │
│    "trials": [                                                   │
│      {                                                           │
│        "trial_number": 1,                                        │
│        "scenario": "Scenario 1",                                 │
│        "option_a_prob": 60,                                      │
│        "option_a_value": 150,                                    │
│        "option_b_prob": 45,                                      │
│        "option_b_value": 180,                                    │
│        "choice": "A",                                            │
│        "reaction_time_ms": 3420,                                 │
│        "confidence": 5                                           │
│      },                                                          │
│      ... (30 trials total)                                       │
│    ],                                                            │
│    "strategy": {                                                 │
│      "risk_preference": 4,                                       │
│      "calculation_method": "mental_math",                        │
│      "confidence_overall": 5                                     │
│    }                                                             │
│  }                                                               │
│                                                                  │
│  ✓ 12 complete response datasets                                │
│  ✓ Each with 30 decision trials                                 │
│  ✓ Includes demographics and strategy info                      │
│  ✓ Reaction times range: 1500-8000ms                            │
│  ✓ Confidence ratings: 1-7 scale                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Statistical Summary

### User Distribution
```
Role          Count   Percentage
─────────────────────────────────
Researcher      1       6.7%
Instructor      1       6.7%
Participants   12      86.6%
─────────────────────────────────
TOTAL          14     100.0%
```

### Signup Status Distribution
```
Status        Count   Percentage
─────────────────────────────────
Attended       12      52.2%
No-Show         2       8.7%
Cancelled       1       4.3%
Booked          8      34.8%
─────────────────────────────────
TOTAL          23     100.0%
```

### Timeslot Utilization
```
Category            Count   Capacity   Utilization
────────────────────────────────────────────────────
Total Timeslots       45       90        25.6%
Past Timeslots        15       30        50.0%
Future Timeslots      30       60        13.3%
```

### Credit Distribution
```
Credits Earned    Student Count
───────────────────────────────
0.0 credits            9
0.5 credits            2
1.0 credits            1
───────────────────────────────
Average: 0.42 credits
Required: 3.0 credits
Completion: 14% average
```

## 🔄 Data Relationships

### One-to-Many Relationships
- **Researcher → Studies**: 1 researcher has 1 study
- **Instructor → Courses**: 1 instructor has 1 course
- **Study → Timeslots**: 1 study has 45 timeslots
- **Timeslot → Signups**: Each timeslot has 0-2 signups
- **Study → Responses**: 1 study has 12 protocol responses
- **Course → Enrollments**: 1 course has 12 enrollments
- **Participant → Signups**: Each participant has 0-2 signups
- **Participant → Credits**: Each participant has 0-2 transactions

### Many-to-Many Relationships (via intermediary models)
- **Participants ↔ Courses** (via Enrollment)
- **Participants ↔ Studies** (via Signup)

## 🎯 Realistic Scenarios Covered

### ✅ Complete Participation Flow
1. Student enrolls in course (PSYC-101)
2. Student views available studies
3. Student reads study description and consent
4. Student books timeslot
5. Student attends session
6. Researcher marks attendance
7. Credits automatically awarded
8. Credits tracked toward course requirement

### ✅ Various Attendance Outcomes
- **Attended**: Study completed, credits awarded
- **No-Show**: Study not completed, no-show count incremented
- **Cancelled**: Timeslot freed up, no penalty
- **Booked**: Future appointment confirmed

### ✅ Research Data Collection
- Protocol responses submitted anonymously
- Session IDs tracked (not linked to identifiable info)
- Rich structured data (demographics, trials, strategy)
- Timestamped submission records

### ✅ Administrative Oversight
- IRB approval tracking with expiration dates
- OSF integration for transparency
- Bayesian monitoring for sequential analysis
- Audit trail via credit transactions

## 📝 Data Integrity

### Enforced Constraints
- ✅ One profile per user (OneToOne)
- ✅ One signup per participant per timeslot (unique_together)
- ✅ Capacity limits enforced (validation)
- ✅ Email uniqueness (unique constraint)
- ✅ Consent recorded at signup time (versioned)

### Audit Trail
- ✅ All models have timestamps (created_at, updated_at)
- ✅ Credit transactions record granting authority
- ✅ Signups record multiple timestamps (booked, cancelled, attended)
- ✅ Consent text versioned at time of signup

### Data Privacy
- ✅ Protocol responses use session IDs (not user IDs)
- ✅ Researcher notes separate from participant notes
- ✅ No identifying info in response payloads

---

## 🚀 Ready to Explore!

The demo data provides a realistic, working example of:
- **Multi-role user system** (researcher, instructor, participants)
- **Complete study lifecycle** (creation → booking → attendance → credits)
- **Research data collection** (protocol responses with rich structure)
- **Administrative tracking** (IRB, OSF, Bayesian monitoring)
- **Course credit management** (enrollment, requirements, progress)

**Next Steps:**
1. Log in with different accounts to see role-specific views
2. Explore the data in Django admin
3. Test workflows (booking, attendance, credits)
4. Review protocol responses
5. Check Bayesian monitoring features

Enjoy the demo! 🎉

