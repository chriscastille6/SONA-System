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
- **Password:** 3Tw3dAJRhAhc

### Dr. Juliann Allen (IRB Reviewer)
- **Email:** juliann.allen@nicholls.edu  
- **Password:** Imtgua2nlkqo

## How to Access Assigned IRBs

1. Log in at the URL above using your email and password.
2. After logging in, go to **Protocol Submissions** (or **IRB** → **Protocol Submissions**) to see your assigned protocols.
3. **Dr. Murphy:** You will see protocols where you are the College of Business representative (assigned automatically when researchers from your college submit).
4. **Dr. Allen:** You will see protocols where you have been assigned as a reviewer. For expedited or full-board reviews, the college rep or chair assigns reviewers—you will receive an email when assigned.

**Note:** Please change your password after your first login for security. Use the “Forgot password?” link on the login page if needed.

If you have any questions or trouble accessing the system, please contact [IRB contact].

Best regards,  
[Your name]

---

## Access to New IRBs

| Role | Access to new submissions |
|------|---------------------------|
| **Dr. Murphy (College Rep)** | Automatically assigned to new protocols from College of Business researchers. He will see them as soon as they are submitted. |
| **Dr. Allen (IRB Reviewer)** | Assigned only when the college rep or chair explicitly assigns her as a reviewer (for expedited or full-board reviews). She will not see new submissions until assigned. |

If you have submitted new protocols and want Juliann to review them, assign her as a reviewer on each protocol (as college rep or chair, use the "Assign Reviewers" action on the protocol detail page).

---

## Server Setup (Run Once)

On the server (bayoupal), run:

```bash
cd ~/hsirb-system && source venv/bin/activate
python manage.py invite_irb_reviewers
```

This will:
- Fix Jon Murphy’s email (jon.murphy@nicholls.edu → jonathan.murphy@nicholls.edu)
- Ensure Juliann Allen has an account
- Set temporary passwords for both
- Print the credentials to copy into the email above
