# IRB Invite Email Draft

**Subject:** Human Subjects IRB – Login Credentials & Assigned Protocols

---

**To:** Dr. Jonathan Murphy (jonathan.murphy@nicholls.edu), Dr. Juliann Allen (juliann.allen@nicholls.edu)

**From:** [Your name/IRB contact]

---

Dear Dr. Murphy and Dr. Allen,

You have been added as IRB reviewers for the Human Subjects IRB system. Below are your login credentials and how to access your assigned protocols.

## Login Information

**Website:** https://bayoupal.nicholls.edu/hsirb/accounts/login/

### Dr. Jonathan Murphy (College of Business Representative)
- **Email:** jonathan.murphy@nicholls.edu  
- **Password:** [*Insert password from `invite_irb_reviewers` output*]

### Dr. Juliann Allen (IRB Reviewer)
- **Email:** juliann.allen@nicholls.edu  
- **Password:** [*Insert password from `invite_irb_reviewers` output*]

## How to Access Assigned IRBs

1. Log in at the URL above using your email and password.
2. After logging in, go to the **Committee Dashboard** or **My Assignments**.
3. Your assigned protocols will appear there for review and approval.

**Note:** Please change your password after your first login for security. Use the “Forgot password?” link on the login page if needed.

If you have any questions or trouble accessing the system, please contact [IRB contact].

Best regards,  
[Your name]

---

## Server Setup (Run Once)

On the server (bayoupal), run:

```bash
cd /path/to/hsirb  # or your project root
python manage.py invite_irb_reviewers
```

This will:
- Fix Jon Murphy’s email (jon.murphy@nicholls.edu → jonathan.murphy@nicholls.edu)
- Ensure Juliann Allen has an account
- Set temporary passwords for both
- Print the credentials to copy into the email above
