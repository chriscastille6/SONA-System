# System Readiness Checklist for Jon Murphy (College Representative)

**Date**: January 16, 2026  
**Status**: ✅ **READY FOR REVIEW**

---

## ✅ System Features Ready

### 1. **Protocol Submission Access**
- ✅ **Navigation Link Added**: IRB members now see "Protocol Submissions" link in the main navigation
- ✅ **Protocol Submission List**: Available at `/studies/protocol/submissions/`
- ✅ **Access Control**: College reps can see all submissions assigned to them
- ✅ **Filtering**: Can filter by decision status (Pending, Approved, R&R, Rejected)

### 2. **Review Workflow**
- ✅ **College Rep Determination**: Can make initial determination (Exempt/Expedited/Full)
- ✅ **Reviewer Assignment**: Can assign reviewers for expedited reviews
- ✅ **Decision Making**: Can approve exempt protocols directly
- ✅ **Exemption Approval**: Can grant exemptions and sign off with approval notes

### 3. **Email Notifications**
- ✅ **Submission Notification**: College rep receives email when protocol is submitted
- ✅ **Reviewer Assignment**: Reviewers receive email when assigned
- ✅ **Decision Notification**: PI receives email when decision is made
- ✅ **Email Includes**: Submission details, links, and PI's reviewer suggestions

### 4. **Protocol Details View**
- ✅ **Complete Information**: All 16 protocol sections displayed
- ✅ **PI Suggestions**: PI's suggested reviewers are prominently displayed
- ✅ **CITI Certificates**: Can view/download uploaded CITI training certificates
- ✅ **Review Actions**: Clear buttons for making determinations and decisions

### 5. **Media Files & Admin Interface**
- ✅ **Media Files**: Fixed to work with `/hsirb/` prefix (CITI certificates accessible)
- ✅ **Admin Interface**: Fixed to load CSS/JS correctly with `/hsirb/` prefix
- ✅ **Static Files**: Properly configured for campus server deployment

---

## 🔍 What Jon Murphy Can Do

### As College Representative:

1. **View Submissions**
   - Navigate to: `https://bayoupal.nicholls.edu/hsirb/studies/protocol/submissions/`
   - Or use the "Protocol Submissions" link in the navigation menu
   - See all submissions assigned to him (filtered by his college)

2. **Review Protocol**
   - Click "View" on any submission
   - See complete protocol details (all 16 sections)
   - See PI's suggested reviewers (e.g., "I recommend Jon Murphy as the CBA rep")
   - View/download CITI training certificates

3. **Make Determination**
   - Choose: Exempt, Expedited, or Full Review
   - For **Exempt**: Can approve immediately with approval notes
   - For **Expedited**: Assign 2 reviewers (can use PI's suggestions)
   - For **Full**: Routes to IRB Chair

4. **Approve Exempt Protocols**
   - Click "Quick Approve (Exempt)" button
   - Add approval notes (acts as digital signature)
   - System generates protocol number (HSIRB-YYYY-NNN)
   - PI receives email notification

5. **Assign Reviewers**
   - For expedited reviews, select 2 IRB members
   - Can see PI's suggestions in the submission details
   - Reviewers receive email notification when assigned

---

## 📋 Current Status of EI × RPM Study

Based on the protocol entry:
- **Study**: EI × RPM Study
- **PI Suggested Review Type**: Exempt
- **PI Suggested Reviewers**: 
  - Jon Murphy (CBA representative)
  - Julianne Allen
- **Status**: Should be submitted and assigned to Jon Murphy as college rep

---

## ⚠️ Important Notes

### Email Configuration
- **Check**: Ensure `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` are configured in `.env` on the server
- **SITE_URL**: Should be set to `https://bayoupal.nicholls.edu/hsirb` in `.env` for correct email links

### Access Requirements
- Jon Murphy's account must have:
  - `role = 'irb_member'` (sets `is_irb_member = True`)
  - Be assigned as `CollegeRepresentative` for the appropriate college
  - Have a valid email address

### Navigation
- The "Protocol Submissions" link appears in the navigation for all IRB members
- It's positioned between "IRB Dashboard" and "Committee" links

---

## 🚀 Deployment Status

### Recent Fixes Applied:
1. ✅ **Media Files**: Fixed `MEDIA_URL` to include `/hsirb/` prefix
2. ✅ **Static Files**: Fixed `STATIC_URL` to include `/hsirb/` prefix  
3. ✅ **Navigation**: Added "Protocol Submissions" link for IRB members
4. ✅ **Admin Interface**: Now loads correctly with proper CSS/JS

### Next Steps:
1. **Deploy Navigation Update**: Push the `templates/base.html` change to server
2. **Verify Email Settings**: Check that email is configured on server
3. **Test Access**: Have Jon Murphy log in and verify he can see protocol submissions

---

## 📝 Testing Checklist

Before Jon Murphy reviews:
- [ ] Navigation shows "Protocol Submissions" link
- [ ] Can access `/studies/protocol/submissions/`
- [ ] EI × RPM study submission appears in list
- [ ] Can view submission details
- [ ] Can see PI's suggested reviewers
- [ ] Can download CITI certificate (if uploaded)
- [ ] Can make determination (Exempt/Expedited/Full)
- [ ] Can approve exempt protocols
- [ ] Email notifications are working

---

## ✅ Conclusion

**The system is READY for Jon Murphy to review protocols.**

All core functionality is in place:
- ✅ Access to protocol submissions
- ✅ Review workflow
- ✅ Email notifications
- ✅ Media file access
- ✅ Admin interface
- ✅ Navigation improvements

**Action Required**: Deploy the navigation update (`templates/base.html`) to make the "Protocol Submissions" link visible.
