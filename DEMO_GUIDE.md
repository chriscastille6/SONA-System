# SONA System Demo Guide

Your SONA system is now populated with demo data and ready to explore!

## 🌐 Access the System

**URL:** http://localhost:8000

## 👤 Demo Accounts

### Researcher Account
- **Email:** researcher@nicholls.edu
- **Password:** demo123
- **Name:** Dr. Sarah Martinez
- **Department:** Psychology, Cognitive Neuroscience Lab

### Instructor Account
- **Email:** instructor@nicholls.edu
- **Password:** demo123
- **Name:** Dr. James Thompson
- **Department:** Psychology

### Participant Accounts (Sample)
All participants have password: `demo123`

- emily.johnson@my.nicholls.edu - Emily Johnson
- michael.brown@my.nicholls.edu - Michael Brown
- sophia.davis@my.nicholls.edu - Sophia Davis
- james.wilson@my.nicholls.edu - James Wilson
- olivia.garcia@my.nicholls.edu - Olivia Garcia
- william.martinez@my.nicholls.edu - William Martinez
- ava.rodriguez@my.nicholls.edu - Ava Rodriguez
- alexander.lee@my.nicholls.edu - Alexander Lee
- isabella.walker@my.nicholls.edu - Isabella Walker
- ethan.hall@my.nicholls.edu - Ethan Hall
- mia.young@my.nicholls.edu - Mia Young
- daniel.king@my.nicholls.edu - Daniel King

## 📚 Demo Data Overview

### Study: "Decision Making Under Uncertainty"
- **Type:** In-Person Lab Study
- **Location:** Psychology Building, Room 215
- **Duration:** 30 minutes
- **Credit Value:** 0.5 credits
- **IRB Status:** Approved (IRB-2025-089)
- **OSF Integration:** Enabled (https://osf.io/8xk2d/)
- **Bayesian Monitoring:** Enabled (threshold: BF > 10)
- **Min Sample Size:** 30 participants

### Course: PSYC-101 - Introduction to Psychology
- **Term:** 2025-Fall
- **Section:** 01
- **Instructor:** Dr. James Thompson
- **Credits Required:** 3.0
- **Enrolled Students:** 12

### Timeslots
- **Total:** 45 sessions
- **Past Sessions:** ~15 (with attendance records)
- **Upcoming Sessions:** ~30 (some with bookings)
- **Capacity:** 2 participants per slot

### Signups
- **Total:** 23 signups
- **Attended:** ~12 signups (80% of past sessions)
- **No-Shows:** ~2 signups (15% of past sessions)
- **Cancelled:** ~1 signup (5% of past sessions)
- **Booked (Future):** 8 upcoming appointments

### Credits
- **Total Transactions:** 15 credits awarded
- **Value:** 0.5 credits per completed study
- Students have earned between 0-1.0 credits toward their 3.0 requirement

### Protocol Responses
- **Total:** 12 complete data sets
- Each contains:
  - Demographics (age, gender, major)
  - 30 decision-making trials
  - Reaction times and confidence ratings
  - Post-study strategy questionnaire

## 🔍 What to Explore

### As a Researcher (Dr. Sarah Martinez)

1. **Researcher Dashboard** - View your active studies
2. **Study Details** - See signup statistics and protocol responses
3. **Timeslot Management** - View upcoming sessions and attendance
4. **Mark Attendance** - Update participant attendance status
5. **View Roster** - See all participants who signed up
6. **Study Status** - Check Bayesian monitoring results
7. **OSF Integration** - See connected OSF project

### As an Instructor (Dr. James Thompson)

1. **My Courses** - View PSYC-101 course
2. **Course Enrollments** - See list of 12 enrolled students
3. **Student Progress** - Check credits earned by each student
4. **Credits Dashboard** - Monitor overall credit distribution

### As a Participant (Any student account)

1. **Available Studies** - Browse studies you're eligible for
2. **Study Details** - Read full description and consent form
3. **Book Timeslot** - Sign up for available session
4. **My Bookings** - View your upcoming appointments
5. **My Credits** - Check credits earned and remaining
6. **Cancel Booking** - Cancel appointments (if within window)

### Admin Features

Access Django admin at: http://localhost:8000/admin/

You can use the superuser account if you've created one, or create one with:
```bash
python manage.py createsuperuser
```

## 📊 Realistic Demo Features

### 1. **Mixed Attendance Records**
- Past sessions show realistic mix of attendance statuses
- Some no-shows recorded (affecting participant records)
- Some cancellations (within cancellation window)

### 2. **Credit Tracking**
- Credits automatically awarded for attended sessions
- Transaction history maintained
- Progress toward course requirement tracked

### 3. **Protocol Responses**
- Realistic decision-making data
- Structured JSON with nested trial data
- Reaction times, confidence ratings, demographics

### 4. **Varied Timeslots**
- Past sessions for viewing historical data
- Upcoming sessions for testing booking flow
- Some slots full, some available
- Different times of day (10am, 2pm, 4pm)

### 5. **IRB & OSF Integration**
- IRB approval status and expiration tracking
- OSF project linked
- Consent form versioning

## 🧪 Test Scenarios

### Scenario 1: Book a Study Session
1. Log in as a participant (e.g., emily.johnson@my.nicholls.edu)
2. View available studies
3. Select "Decision Making Under Uncertainty"
4. Review description and consent
5. Choose an available timeslot
6. Confirm booking
7. View confirmation in "My Bookings"

### Scenario 2: Mark Attendance
1. Log in as researcher (researcher@nicholls.edu)
2. Go to Researcher Dashboard
3. Select your study
4. Click "Mark Attendance"
5. Select a past timeslot
6. Mark participants as attended/no-show
7. Credits automatically awarded to attended participants

### Scenario 3: View Student Progress
1. Log in as instructor (instructor@nicholls.edu)
2. Go to "My Courses"
3. Select PSYC-101
4. View enrolled students
5. See credits earned by each student
6. Check who needs more credits

### Scenario 4: Cancel a Booking
1. Log in as a participant with future booking
2. Go to "My Bookings"
3. Select an upcoming appointment
4. Cancel the booking (if within cancellation window)
5. Verify the slot becomes available again

### Scenario 5: View Research Data
1. Log in as researcher
2. Go to your study
3. View protocol responses (12 complete datasets)
4. Export data (if implemented)
5. Check Bayesian monitoring status

## 📈 Data to Review

### Study Analytics
- Total signups: 23
- Attendance rate: ~80%
- No-show rate: ~15%
- Cancellation rate: ~5%
- Protocol responses: 12

### Credit Distribution
- Average credits earned: ~1.25 credits
- Range: 0.0 - 1.0 credits (out of 3.0 required)
- Total credits awarded: 7.5 credits (15 × 0.5)

### Timeslot Utilization
- Total capacity: 90 slots (45 timeslots × 2 capacity)
- Booked: 23 (25.6% utilization)
- Available: 67 slots remaining

## 🎯 Next Steps

1. **Explore the interface** - Try all three user roles
2. **Test workflows** - Book studies, mark attendance, view credits
3. **Review data structures** - Check protocol responses and transaction history
4. **Test edge cases** - Try canceling past bookings, overbooking, etc.
5. **Customize study** - Modify the demo study or create new ones
6. **Add more participants** - Expand the participant pool
7. **Create additional studies** - Build diverse study catalog

## 🔧 Reset Demo Data

To start fresh:
```bash
python manage.py flush  # Clear all data
python manage.py migrate  # Recreate tables
python manage.py create_demo_data  # Recreate demo data
```

## 📝 Notes

- All timestamps are relative to the current date
- Email verification is pre-completed for all demo accounts
- No-show counts are tracked in participant profiles
- Consent text is versioned and stored with each signup
- All credit transactions are auditable with timestamps

---

**Enjoy exploring the SONA System!** 🎉

If you have questions or need modifications, just let me know.

