# Testing as Jon Murphy (College Representative)

## ✅ Test User Created

**Login Credentials:**
- **Email**: `jon.murphy@test.local`
- **Password**: `testpass123`
- **Role**: IRB Member
- **College Representative**: College of Business Administration

---

## 🚀 Quick Start

### 0. Run Migrations (if needed)

If you haven't run migrations recently, make sure all protocol submission migrations are applied:

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py migrate
```

### 1. Start the Development Server

```bash
cd "/Users/ccastille/Documents/GitHub/SONA System"
source venv/bin/activate
python manage.py runserver
```

### 2. Log In as Jon Murphy

1. Go to: http://localhost:8000/accounts/login/
2. Enter:
   - Email: `jon.murphy@test.local`
   - Password: `testpass123`

### 3. Access Protocol Submissions

Once logged in, you should see:
- **"IRB Dashboard"** link in navigation
- **"Protocol Submissions"** link in navigation (NEW!)
- **"Committee"** link in navigation

Click **"Protocol Submissions"** to see all submissions assigned to you.

---

## 📋 Testing Scenarios

### Scenario 1: View Protocol Submissions List

1. Navigate to: http://localhost:8000/studies/protocol/submissions/
2. You should see:
   - Any protocol submissions assigned to you (as College of Business Administration rep)
   - Filter by decision status (Pending, Approved, etc.)
   - Submission details (Study, PI, Review Type, Decision, etc.)

### Scenario 2: Review a Protocol Submission

1. Click "View" on any submission
2. You should see:
   - Complete protocol details (all 16 sections)
   - PI's suggested reviewers (if provided)
   - CITI training certificate (if uploaded)
   - Review assignment information
   - Action buttons for making determinations

### Scenario 3: Make a Determination

**For Exempt Protocols:**
1. Click "Make Determination" or "Quick Approve (Exempt)"
2. Choose: **Exempt**
3. Add approval notes (acts as digital signature)
4. Click "Approve Protocol"
5. System generates protocol number (HSIRB-YYYY-NNN)
6. PI receives email notification

**For Expedited Protocols:**
1. Click "Make Determination"
2. Choose: **Expedited**
3. System prompts you to assign 2 reviewers
4. Select reviewers (can use PI's suggestions)
5. Reviewers receive email notifications

**For Full Board Protocols:**
1. Click "Make Determination"
2. Choose: **Full**
3. System routes to IRB Chair automatically

### Scenario 4: Assign Reviewers (Expedited Review)

1. After making "Expedited" determination
2. Click "Assign Reviewers"
3. Select 2 IRB members from the list
4. Click "Assign Reviewers"
5. Reviewers receive email notifications

---

## 🧪 Creating a Test Protocol Submission

If you don't have a protocol submission to test with, you can:

### Option 1: Use Existing EI × RPM Study

If the EI × RPM study has a protocol submission:

1. **Check if it's assigned to you:**
   - The study researcher's department determines which college rep gets assigned
   - For Business Administration → You (Jon Murphy)
   - For Education → Grant Gautreaux
   - etc.

2. **Manually assign a submission to you (via Django shell):**
   ```python
   python manage.py shell
   ```
   ```python
   from apps.studies.models import ProtocolSubmission
   from apps.accounts.models import User
   
   # Get your test user
   jon = User.objects.get(email='jon.murphy@test.local')
   
   # Get a protocol submission
   submission = ProtocolSubmission.objects.filter(status='submitted').first()
   
   # Assign it to you
   if submission:
       submission.college_rep = jon
       submission.save()
       print(f"Assigned submission {submission.submission_number} to Jon Murphy")
   ```

### Option 2: Create a New Test Submission

1. **Log in as a researcher** (create one if needed):
   ```bash
   python manage.py shell
   ```
   ```python
   from apps.accounts.models import User, Profile
   
   # Create researcher
   researcher = User.objects.create_user(
       email='researcher@test.local',
       password='testpass123',
       first_name='Test',
       last_name='Researcher',
       role='researcher'
   )
   
   # Set department (Business Administration → assigns to Jon Murphy)
   profile, _ = Profile.objects.get_or_create(user=researcher)
   profile.department = 'Business'  # or 'Accounting', 'Finance', etc.
   profile.save()
   ```

2. **Log in as researcher** and:
   - Create a study
   - Enter protocol information (draft)
   - Submit for review
   - It should automatically assign to you (Jon Murphy) if researcher's department is Business

---

## 🔍 What to Test

### Navigation & Access
- [ ] Can see "Protocol Submissions" link in navigation
- [ ] Can access `/studies/protocol/submissions/`
- [ ] Can see submissions assigned to you
- [ ] Can filter by decision status

### Protocol Review
- [ ] Can view complete protocol details
- [ ] Can see PI's suggested reviewers
- [ ] Can download/view CITI certificates
- [ ] Can see all 16 protocol sections

### Review Workflow
- [ ] Can make determination (Exempt/Expedited/Full)
- [ ] Can approve exempt protocols
- [ ] Can assign reviewers for expedited reviews
- [ ] Can add approval notes
- [ ] System generates protocol numbers on approval

### Email Notifications
- [ ] Receive email when protocol is submitted (if email configured)
- [ ] Reviewers receive email when assigned (if email configured)
- [ ] PI receives email when decision is made (if email configured)

---

## 🐛 Troubleshooting

### "No protocol submissions found"
- **Cause**: No submissions assigned to you
- **Fix**: Create a test submission or manually assign one (see Option 1 above)

### "Access denied" errors
- **Cause**: User role not set correctly
- **Fix**: Run `python manage.py create_test_jon_murphy` again

### Can't see "Protocol Submissions" link
- **Cause**: Navigation template not updated
- **Fix**: Make sure `templates/base.html` has the new link (should be there)

### Protocol not auto-assigned to you
- **Cause**: Researcher's department doesn't map to Business Administration
- **Fix**: Set researcher's profile department to 'Business', 'Accounting', or 'Finance'

---

## 📝 Notes

- **Email notifications** will only work if email is configured in `.env`
- **Local testing** uses `localhost:8000` (no `/hsirb/` prefix needed)
- **Media files** (CITI certificates) should work locally without special configuration
- **Admin access**: Jon Murphy doesn't have admin access by default (can add `--staff` flag if needed)

---

## ✅ Success Criteria

You've successfully tested as Jon Murphy if you can:
1. ✅ Log in with the test credentials
2. ✅ See "Protocol Submissions" in navigation
3. ✅ View at least one protocol submission
4. ✅ Make a determination on a submission
5. ✅ Approve an exempt protocol (if applicable)

---

**Happy Testing!** 🎉
