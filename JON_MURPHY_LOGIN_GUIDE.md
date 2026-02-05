# Jon Murphy Login Guide

## Login Credentials

**Email:** `jon.murphy@nicholls.edu`  
**Password:** `temp_password_change_me`

⚠️ **Important:** Jon should change this password after first login!

## Login Steps

1. **Go to the login page:**
   - URL: https://bayoupal.nicholls.edu/hsirb/accounts/login/

2. **Enter credentials:**
   - Email: `jon.murphy@nicholls.edu`
   - Password: `temp_password_change_me`

3. **After login:**
   - Jon will be automatically redirected to the **IRB Member Dashboard**
   - URL: https://bayoupal.nicholls.edu/hsirb/studies/irb/member/dashboard/

## What Jon Can Access

### IRB Member Dashboard
- View all protocol submissions assigned to him
- See pending reviews
- Access his assigned submissions

### Protocol Submissions
- URL: https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/
- View all submissions where he is the college representative
- Make determinations (Exempt/Expedited/Full Board)
- Approve exempt protocols
- Assign reviewers for expedited protocols

### Individual Protocol Details
- Click any submission to view full details
- See all uploaded documents (protocol PDF, CITI certificates, etc.)
- Make approval decisions
- Add notes and signatures

## Troubleshooting

### If Login Fails

1. **Verify account exists:**
   ```bash
   # On server, run:
   python manage.py shell -c "
   from apps.accounts.models import User
   jon = User.objects.filter(email='jon.murphy@nicholls.edu').first()
   if jon:
       print(f'✓ Account exists: {jon.get_full_name()}')
       print(f'  Email: {jon.email}')
       print(f'  Role: {jon.role}')
       print(f'  Active: {jon.is_active}')
       print(f'  Staff: {jon.is_staff}')
   else:
       print('✗ Account not found')
   "
   ```

2. **Reset password (if needed):**
   ```bash
   # On server, run:
   python manage.py shell -c "
   from apps.accounts.models import User
   jon = User.objects.filter(email='jon.murphy@nicholls.edu').first()
   if jon:
       jon.set_password('temp_password_change_me')
       jon.save()
       print('✓ Password reset')
   "
   ```

3. **Check account status:**
   - Ensure `is_active = True`
   - Ensure `role = 'irb_member'`
   - Ensure email is exactly `jon.murphy@nicholls.edu`

### If Redirect Doesn't Work

- Manually navigate to: https://bayoupal.nicholls.edu/hsirb/studies/irb/member/dashboard/
- Or go to: https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/

## First-Time Login Checklist

- [ ] Log in with temporary password
- [ ] Change password to a secure one
- [ ] Verify access to IRB Member Dashboard
- [ ] Check that protocol submissions are visible
- [ ] Test viewing a protocol submission detail page

## Quick Links for Jon

- **Login:** https://bayoupal.nicholls.edu/hsirb/accounts/login/
- **IRB Dashboard:** https://bayoupal.nicholls.edu/hsirb/studies/irb/member/dashboard/
- **Protocol Submissions:** https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/
- **Profile:** https://bayoupal.nicholls.edu/hsirb/accounts/profile/
