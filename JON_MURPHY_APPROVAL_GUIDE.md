# Jon Murphy IRB Approval Guide

## Jon Murphy's Access

### Login Credentials
- **Email**: `jon.murphy@nicholls.edu`
- **Password**: `temp_password_change_me` (should be changed)
- **Role**: IRB Member
- **College Representative**: Business Administration

### What Jon Murphy Can Do

1. **View Protocol Submissions**
   - Access: https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/
   - Can see all submissions assigned to him as college rep

2. **Make Initial Determination**
   - For pending protocols, can determine review type:
     - Exempt
     - Expedited Review
     - Full Board Review

3. **Approve Exempt Protocols**
   - If determination is "Exempt", Jon Murphy can approve immediately
   - Can grant exemption and assign protocol number
   - Can add approval notes/signature

4. **Assign Reviewers (for Expedited)**
   - Can assign 2 reviewers for expedited review protocols

### Approval Workflow

1. **Log in** as Jon Murphy
2. **Go to Protocol Submissions**: https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/
3. **Click on a submission** to view details
4. **Make determination** (if not already done):
   - Select review type: Exempt/Expedited/Full
   - Add notes
   - Submit determination
5. **Approve (if Exempt)**:
   - If exempt, an "Approve and Grant Exemption" button will appear
   - Enter approval notes/signature
   - Click to approve
   - Protocol number will be auto-generated

### Current TRO Study Status

The TRO study protocol is already marked as "approved" in the database, but Jon Murphy can:
- View the submission details
- See the approval that was recorded
- Access all documents (approval PDF, protocol PDF, CITI certificate)

### To Test Jon Murphy's Access

```bash
# On server, check Jon Murphy's account
python manage.py shell -c "
from apps.accounts.models import User
from apps.studies.models import ProtocolSubmission, CollegeRepresentative

jon = User.objects.filter(email__icontains='murphy').first()
if jon:
    print(f'Email: {jon.email}')
    print(f'Role: {jon.role}')
    print(f'Active: {jon.is_active}')
    
    # Check college rep assignment
    rep = CollegeRepresentative.objects.filter(representative=jon).first()
    if rep:
        print(f'College Rep: {rep.get_college_display()}')
    
    # Check assigned submissions
    submissions = ProtocolSubmission.objects.filter(college_rep=jon)
    print(f'Assigned Submissions: {submissions.count()}')
    for s in submissions:
        print(f'  - {s.submission_number}: {s.study.title} ({s.decision})')
"
```

### URLs for Jon Murphy

- **Login**: https://bayoupal.nicholls.edu/hsirb/accounts/login/
- **Protocol Submissions**: https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/
- **IRB Member Dashboard**: https://bayoupal.nicholls.edu/hsirb/studies/irb/member/dashboard/
