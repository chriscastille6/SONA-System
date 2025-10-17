# 🚀 SONA System Demo - Quick Start

Your SONA system is now fully populated with realistic demo data and ready to explore!

## ⚡ Quick Access

### 🌐 System URL
**http://localhost:8000**

### 🔑 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Researcher** | researcher@nicholls.edu | demo123 |
| **Instructor** | instructor@nicholls.edu | demo123 |
| **Student** | emily.johnson@my.nicholls.edu | demo123 |
| **Student** | michael.brown@my.nicholls.edu | demo123 |

> 💡 **Tip:** All 12 participant accounts use the same password: `demo123`

## 📊 What's Included

✅ **1 Research Study**
- Title: "Decision Making Under Uncertainty"
- 45 timeslots (past and future)
- IRB approved with OSF integration
- Bayesian monitoring enabled

✅ **1 Course**
- PSYC-101: Introduction to Psychology
- 12 enrolled students
- 3.0 credits required

✅ **15 Users**
- 1 Researcher
- 1 Instructor
- 12 Participants (students)

✅ **23 Signups**
- 12 attended (credits awarded)
- 2 no-shows
- 1 cancelled
- 8 future bookings

✅ **12 Protocol Responses**
- Complete decision-making datasets
- 30 trials per participant
- Demographics and strategy data

## 🎯 5-Minute Tour

### 1️⃣ As a Researcher (2 minutes)
```
1. Go to http://localhost:8000
2. Log in: researcher@nicholls.edu / demo123
3. Click "Researcher Dashboard"
4. View your study: "Decision Making Under Uncertainty"
5. Click "Mark Attendance" to see past sessions
6. Click "View Roster" to see all participants
7. Notice 12 protocol responses collected
```

**What to look for:**
- Study statistics and signup counts
- Attendance records (attended, no-show)
- Credit transactions automatically created
- Protocol response data

### 2️⃣ As an Instructor (1 minute)
```
1. Log out (top right)
2. Log in: instructor@nicholls.edu / demo123
3. Click "My Courses"
4. Select "PSYC-101"
5. View enrolled students and their credit progress
```

**What to look for:**
- 12 enrolled students
- Credit balances (0.0 - 1.0 earned of 3.0 required)
- Individual student progress tracking

### 3️⃣ As a Participant (2 minutes)
```
1. Log out
2. Log in: emily.johnson@my.nicholls.edu / demo123
3. Click "Available Studies"
4. Click on "Decision Making Under Uncertainty"
5. Read the study description
6. Try to book an available timeslot
7. Click "My Bookings" to see your appointments
8. Click "My Credits" to see your progress
```

**What to look for:**
- Study description and consent form
- Available timeslots with capacity
- Your current credit balance
- Credits needed to complete requirement

## 📚 Documentation

Three detailed guides are available:

1. **DEMO_GUIDE.md** - Comprehensive walkthrough
   - All user accounts
   - Detailed feature descriptions
   - Test scenarios and workflows

2. **DEMO_DATA_STRUCTURE.md** - Data architecture
   - Visual data relationship diagrams
   - Statistical summaries
   - Database schema overview

3. **This file** - Quick start essentials

## 🧪 Try These Features

### Participant Features
- ✅ Browse available studies
- ✅ Read study descriptions and consent forms
- ✅ Book timeslots for future sessions
- ✅ View upcoming appointments
- ✅ Check credit balance and progress
- ✅ Cancel bookings (within cancellation window)

### Researcher Features
- ✅ View study dashboard with statistics
- ✅ Manage timeslots (create, edit, cancel)
- ✅ Mark attendance for sessions
- ✅ View participant roster
- ✅ Access protocol responses
- ✅ Monitor Bayesian analysis results
- ✅ Track IRB approval status
- ✅ Link to OSF projects

### Instructor Features
- ✅ View enrolled students
- ✅ Monitor credit progress
- ✅ Track completion rates
- ✅ Review credit transactions

### Admin Features (via Django Admin)
- ✅ Manage all users and profiles
- ✅ Edit studies and courses
- ✅ View audit logs
- ✅ Adjust credit transactions
- ✅ Access all data models

## 🔍 Realistic Demo Features

### ✨ Past Sessions with History
The demo includes 15 completed sessions with:
- Realistic attendance patterns (80% attended)
- No-show tracking (15% no-show rate)
- Cancellations (5% cancelled)
- Automatic credit awards for attendance

### ✨ Future Sessions Available
30 upcoming timeslots for:
- Testing the booking workflow
- Viewing available capacity
- Cancellation scenarios
- Calendar management

### ✨ Rich Research Data
12 complete protocol response datasets with:
- Participant demographics
- 30 decision-making trials each
- Reaction times (1.5-8 seconds)
- Confidence ratings
- Post-study questionnaire

### ✨ Credit Tracking System
Fully functional credit management:
- Automatic credit awards on attendance
- Transaction history with timestamps
- Progress toward course requirement
- Instructor oversight dashboard

## 🛠️ Server Status

Your Django development server should be running at:
**http://localhost:8000**

If it's not running, start it with:
```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py runserver
```

## 🔄 Reset Demo Data

If you want to start fresh:

```bash
# Clear everything
python manage.py flush --no-input

# Recreate demo data
python manage.py create_demo_data
```

## 📈 System Statistics

```
┌─────────────────────────────────────┐
│        DEMO DATA SUMMARY            │
├─────────────────────────────────────┤
│ Users:              15              │
│ Studies:             1              │
│ Courses:             1              │
│ Timeslots:          45              │
│ Signups:            23              │
│ Credits Awarded:    15              │
│ Protocol Responses: 12              │
└─────────────────────────────────────┘
```

## 🎓 Learning Outcomes

After exploring this demo, you'll understand:

1. **Multi-Role System** - How researchers, instructors, and participants interact
2. **Study Lifecycle** - From creation to data collection
3. **Credit Management** - Automatic tracking and requirement fulfillment
4. **Research Integrity** - IRB tracking, consent versioning, OSF integration
5. **Data Collection** - Anonymous protocol responses with rich structure
6. **Attendance Tracking** - Real-time status updates and automated credits
7. **Bayesian Monitoring** - Sequential analysis for early stopping

## 🎉 You're All Set!

The SONA system is fully functional with realistic data. You can:

- ✅ Test all features with real workflows
- ✅ See how different user roles interact
- ✅ Review data collection and storage
- ✅ Understand the complete research participation cycle
- ✅ Explore administrative and oversight features

**Enjoy exploring the system!** If you need to modify or extend the demo data, the command script is located at:
`apps/studies/management/commands/create_demo_data.py`

---

## 💡 Quick Tips

1. **Use different browser profiles** to stay logged in as multiple users simultaneously
2. **Check Django admin** (`/admin/`) for behind-the-scenes data management
3. **Look at the database** directly with: `python manage.py dbshell`
4. **Export data** from protocol responses to analyze in R or Python
5. **Customize the study** to match your research needs

## 📞 Need Help?

- Check the main README.md for system documentation
- Review DEPLOYMENT_SUCCESS.md for deployment notes
- See BAYESIAN_MONITORING_GUIDE.md for analysis features
- Look at IRB_Automation_Toolkit/ for IRB package generation

**Happy exploring!** 🚀

